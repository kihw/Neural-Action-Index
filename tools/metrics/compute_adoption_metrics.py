"""Calcule WAU/MAU, temps moyen de retrieval et taux d'usage resolve.

Usage:
  python tools/metrics/compute_adoption_metrics.py analytics/events.jsonl --as-of 2026-04-05
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean


@dataclass
class Event:
    ts: datetime
    user_id: str
    session_id: str
    event_name: str
    resource_id: str | None


def parse_event(line: str) -> Event | None:
    raw = json.loads(line)
    if not {"ts", "user_id", "session_id", "event_name"}.issubset(raw):
        return None
    return Event(
        ts=datetime.fromisoformat(raw["ts"]),
        user_id=str(raw["user_id"]),
        session_id=str(raw["session_id"]),
        event_name=str(raw["event_name"]),
        resource_id=raw.get("resource_id"),
    )


def load_events(path: Path) -> list[Event]:
    events: list[Event] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        evt = parse_event(line)
        if evt:
            events.append(evt)
    return sorted(events, key=lambda e: e.ts)


def active_users(events: list[Event], since: datetime, until: datetime) -> set[str]:
    return {e.user_id for e in events if since <= e.ts <= until}


def compute_retrieval_time(events: list[Event], since: datetime, until: datetime) -> float | None:
    searches: dict[tuple[str, str], list[datetime]] = defaultdict(list)
    lags: list[float] = []

    for e in events:
        if not (since <= e.ts <= until):
            continue
        key = (e.user_id, e.session_id)
        if e.event_name == "search_submitted":
            searches[key].append(e.ts)
        elif e.event_name in {"resource_opened", "resource_inserted"} and searches[key]:
            start = searches[key].pop(0)
            lags.append((e.ts - start).total_seconds())

    if not lags:
        return None
    return mean(lags)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events_file", type=Path)
    parser.add_argument("--as-of", type=str, default=datetime.utcnow().date().isoformat())
    args = parser.parse_args()

    as_of = datetime.fromisoformat(args.as_of + "T23:59:59")
    wau_since = as_of - timedelta(days=6)
    mau_since = as_of - timedelta(days=29)

    events = load_events(args.events_file)

    wau = len(active_users(events, wau_since, as_of))
    mau = len(active_users(events, mau_since, as_of))
    wau_mau = (wau / mau) if mau else 0.0

    retrieval_avg = compute_retrieval_time(events, mau_since, as_of)

    resolve_calls = sum(1 for e in events if mau_since <= e.ts <= as_of and e.event_name == "resolve_called")
    search_calls = sum(1 for e in events if mau_since <= e.ts <= as_of and e.event_name == "search_submitted")
    resolve_usage = (resolve_calls / search_calls) if search_calls else 0.0

    print(f"as_of={args.as_of}")
    print(f"WAU={wau}")
    print(f"MAU={mau}")
    print(f"WAU/MAU={wau_mau:.2%}")
    print("avg_time_to_retrieve_sec=" + (f"{retrieval_avg:.2f}" if retrieval_avg is not None else "n/a"))
    print(f"resolve_usage_rate={resolve_usage:.2%}")


if __name__ == "__main__":
    main()

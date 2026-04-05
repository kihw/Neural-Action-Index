from __future__ import annotations

import csv
from pathlib import Path


def extract_fields(input_path: str, output_path: str, fields: list[str]) -> None:
    with Path(input_path).open("r", encoding="utf-8", newline="") as src:
        reader = csv.DictReader(src)
        with Path(output_path).open("w", encoding="utf-8", newline="") as dst:
            writer = csv.DictWriter(dst, fieldnames=fields)
            writer.writeheader()
            for row in reader:
                writer.writerow({field: row.get(field, "") for field in fields})

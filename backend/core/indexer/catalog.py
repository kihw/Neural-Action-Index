from __future__ import annotations

from collections import defaultdict
from math import log
from pathlib import Path

from backend.core.indexer.loader import load_resources, validate_resources
from backend.core.schema.models import RecallNode, Resource, SearchHit
from backend.core.search.service import SearchService


class ResourceCatalog:
    def __init__(self, root: Path):
        self.root = root
        self.index_dir = root / "resources" / "index"
        self._resources: dict[str, Resource] = {}
        self._by_tag: dict[str, set[str]] = defaultdict(set)
        self._by_category: dict[str, set[str]] = defaultdict(set)
        self._by_theme: dict[str, set[str]] = defaultdict(set)

    def refresh(self) -> None:
        loaded = load_resources(self.index_dir)
        validate_resources(self.root, loaded)
        self._resources = {resource.id: resource for resource in loaded}
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        self._by_tag.clear()
        self._by_category.clear()
        self._by_theme.clear()

        for resource in self._resources.values():
            self._by_category[resource.category].add(resource.id)
            self._by_theme[resource.theme].add(resource.id)
            for tag in resource.tags:
                self._by_tag[tag].add(resource.id)

    @property
    def resources(self) -> dict[str, Resource]:
        return self._resources

    def by_tag(self, tag: str) -> list[Resource]:
        return [self._resources[resource_id] for resource_id in sorted(self._by_tag.get(tag, set()))]

    def by_category(self, category: str) -> list[Resource]:
        ids = sorted(self._by_category.get(category, set()))
        return [self._resources[resource_id] for resource_id in ids]

    def by_theme(self, theme: str) -> list[Resource]:
        ids = sorted(self._by_theme.get(theme, set()))
        return [self._resources[resource_id] for resource_id in ids]

    def recall(self) -> dict[str, list[RecallNode]]:
        by_type: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)

        for resource in self._resources.values():
            by_type[resource.type.value] += 1
            by_category[resource.category] += 1

        return {
            "types": [RecallNode(key=k, count=v) for k, v in sorted(by_type.items())],
            "categories": [
                RecallNode(key=k, count=v) for k, v in sorted(by_category.items())
            ],
        }

    def tree(self, path: str | None = None) -> dict:
        tree: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for resource in self._resources.values():
            tree[resource.category][resource.theme].append(resource.id)

        normalized = {
            category: {theme: sorted(ids) for theme, ids in themes.items()}
            for category, themes in tree.items()
        }

        if not path:
            return normalized

        parts = path.split("/")
        if len(parts) == 1:
            return {parts[0]: normalized.get(parts[0], {})}
        if len(parts) == 2:
            category, theme = parts
            return {category: {theme: normalized.get(category, {}).get(theme, [])}}

        raise ValueError("path must be either <category> or <category>/<theme>")

    def get(self, resource_id: str) -> Resource:
        try:
            return self._resources[resource_id]
        except KeyError as exc:
            raise KeyError(f"Unknown resource id: {resource_id}") from exc

    def related(self, resource_id: str) -> list[Resource]:
        resource = self.get(resource_id)
        if resource.related:
            return [self.get(related_id) for related_id in resource.related]

        fallback_hits = self.search(
            " ".join([resource.title, resource.description, " ".join(resource.tags)]),
            limit=6,
        )
        related_resources: list[Resource] = []
        for hit in fallback_hits:
            if hit.id == resource.id:
                continue
            related_resources.append(self.get(hit.id))
            if len(related_resources) >= 5:
                break
        return related_resources

    def search(self, query: str, *, limit: int = 20) -> list[SearchHit]:
        terms = [term for term in query.strip().lower().split() if term]
        if not terms:
            return []

        docs: list[tuple[Resource, list[str]]] = []
        document_frequency: dict[str, int] = defaultdict(int)
        for resource in self._resources.values():
            tokens = " ".join(
                [
                    resource.id,
                    resource.title,
                    resource.description,
                    resource.category,
                    resource.theme,
                    " ".join(resource.tags),
                ]
            ).lower().split()
            docs.append((resource, tokens))
            for token in set(tokens):
                document_frequency[token] += 1

        total_docs = len(docs) or 1
        hits: list[SearchHit] = []
        for resource, tokens in docs:
            if not tokens:
                continue
            token_count: dict[str, int] = defaultdict(int)
            for token in tokens:
                token_count[token] += 1

            score = 0.0
            for term in terms:
                tf = token_count.get(term, 0) / len(tokens)
                if tf == 0:
                    continue
                idf = log(1 + (total_docs / (1 + document_frequency.get(term, 0))))
                score += tf * idf

            haystack = " ".join(tokens)
            for term in terms:
                if term in haystack:
                    score += 0.05
                if term in resource.id.lower():
                    score += 0.1
                if term in resource.title.lower():
                    score += 0.1

            if score > 0:
                hits.append(
                    SearchHit(
                        id=resource.id,
                        title=resource.title,
                        type=resource.type,
                        category=resource.category,
                        theme=resource.theme,
                        description=resource.description,
                        score=round(score, 4),
                    )
                )

        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

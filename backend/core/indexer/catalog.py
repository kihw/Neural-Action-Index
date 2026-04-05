from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from backend.core.indexer.loader import load_resources, validate_cross_references
from backend.core.schema.models import RecallNode, Resource, SearchHit


class ResourceCatalog:
    def __init__(self, root: Path):
        self.root = root
        self.index_dir = root / "resources" / "index"
        self._resources: dict[str, Resource] = {}

    def refresh(self) -> None:
        loaded = load_resources(self.index_dir)
        validate_cross_references(loaded)
        self._resources = {resource.id: resource for resource in loaded}

    @property
    def resources(self) -> dict[str, Resource]:
        return self._resources

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
        return [self.get(related_id) for related_id in resource.related]

    def search(self, query: str, *, limit: int = 20) -> list[SearchHit]:
        q = query.strip().lower()
        if not q:
            return []

        hits: list[SearchHit] = []
        for resource in self._resources.values():
            haystack = " ".join(
                [
                    resource.id,
                    resource.title,
                    resource.description,
                    resource.category,
                    resource.theme,
                    " ".join(resource.tags),
                ]
            ).lower()
            if q in haystack:
                score = 0.5
                if q in resource.id.lower():
                    score += 0.25
                if q in resource.title.lower():
                    score += 0.25
                hits.append(
                    SearchHit(
                        id=resource.id,
                        title=resource.title,
                        type=resource.type,
                        category=resource.category,
                        theme=resource.theme,
                        description=resource.description,
                        score=score,
                    )
                )

        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

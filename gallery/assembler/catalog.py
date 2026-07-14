"""
catalog.py - Object catalog from objects_config.json.

Indexes the gallery object config by slug. Operates on an already-parsed
dict: the assembler package never opens files or hits the network itself
(manifest v2 Section 2 boundary rule). In Pyodide the caller supplies the
parsed JSON via a JS fetch; in CPython tests via json.load. Either way the
catalog just indexes.

The catalog is the source of per-object identity and policy (category,
canonical_center/frame, features). The live orbital numbers live in the
served cache, read by cache_reader; the resolver composes the two.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

from typing import Any, Dict

from .errors import UnknownObjectError


class Catalog:
    def __init__(self, config: Dict[str, Any]):
        self._raw = config
        self._by_slug = {}
        for obj in config.get("objects", []):
            slug = obj.get("slug")
            if slug:
                self._by_slug[slug] = obj
        self._defaults = dict(config.get("defaults") or {})

    def has(self, slug: str) -> bool:
        return slug in self._by_slug

    def get(self, slug: str) -> Dict[str, Any]:
        try:
            return self._by_slug[slug]
        except KeyError:
            raise UnknownObjectError(
                "Object '%s' is not in objects_config.json." % slug
            )

    def slugs(self):
        return tuple(self._by_slug.keys())

    @property
    def defaults(self) -> Dict[str, Any]:
        return dict(self._defaults)

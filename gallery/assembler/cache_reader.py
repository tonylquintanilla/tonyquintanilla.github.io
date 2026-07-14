"""
cache_reader.py - Reads the served gallery cache.

The served cache is coverage_index.json (one osculating snapshot + one
as_of_today cross-check point per object, plus spacecraft position arcs and
per-object feature dispatch keys). This module reads that served structure
ONLY. It never imports astroquery, the builder, or anything that queries
Horizons; it never opens files or touches the network (manifest v2 Section 1
governing rule, Section 2 boundary rule). It operates on an already-parsed
dict supplied by the caller.

served_window note: coverage_index.json carries a top-level served_window
field that is currently null at HEAD. Populating it is a small builder change
tracked with F1. Until then served_window() returns None and the resolver
treats the propagation bound as unenforced-but-warned rather than rejecting.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""

from typing import Any, Dict, Optional

from .errors import MissingCachePayloadError, UnknownObjectError


class CacheReader:
    def __init__(self, coverage_index: Dict[str, Any]):
        self._raw = coverage_index
        self._objects = coverage_index.get("objects", {}) or {}
        # A stable id for the snapshot the assembly was built against, so the
        # L-080 fingerprint can detect "same scene, different underlying data."
        self._snapshot_id = str(
            coverage_index.get("generated")
            or coverage_index.get("schema_version")
            or "unknown"
        )

    def snapshot_id(self) -> str:
        return self._snapshot_id

    def served_window(self) -> Optional[Any]:
        return self._raw.get("served_window")

    def scene_features(self):
        return tuple(self._raw.get("scene_features") or ())

    def has(self, slug: str) -> bool:
        return slug in self._objects

    def record(self, slug: str) -> Dict[str, Any]:
        if slug not in self._objects:
            raise UnknownObjectError(
                "Object '%s' has no entry in the served cache "
                "(coverage_index.json)." % slug
            )
        return self._objects[slug]

    def require_orbit_payload(self, slug: str) -> Dict[str, Any]:
        """Return the osculating block for slug, or fail with an
        object-specific diagnostic (Section 7 failure invariant)."""
        rec = self.record(slug)
        osc = rec.get("osculating")
        if not osc:
            raise MissingCachePayloadError(
                "Object '%s' has no osculating payload in the served cache; "
                "cannot build an orbit trace for it." % slug
            )
        return osc

"""
errors.py - Stable exception classes for the solar system assembler.

Every failure the assembler can raise is a named subclass of AssemblerError,
so callers (the Pyodide page, the L-080 harness, tests) can branch on a
stable type rather than parsing message text. Per manifest v2 Section 7's
failure invariants: an unsupported scene must fail BEFORE any partial trace
is built; a missing cache payload must name the offending object.

Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
"""


class AssemblerError(Exception):
    """Base class for every assembler failure."""


class FrameRejectionError(AssemblerError):
    """A scene mixes frames the assembler will not silently transform.

    Phase 2 renders each object in its own stored frame only. Asking for a
    heliocentric scene that includes a parent-relative moon is rejected here,
    before any trace is built (manifest v2 Section 3).
    """


class UnsupportedInPhase2Error(AssemblerError):
    """A recognized scene-spec field is deliberately not implemented yet.

    Distinct from an unknown field (which only warns): these are known
    vocabulary items (shells at spec level, celestial_sphere, animation,
    apsidal/closest-approach spec fields, comet_tails) that must fail loudly
    rather than drop silently (manifest v2 Section 3 disposition table).
    """


class MissingCachePayloadError(AssemblerError):
    """The served cache has no usable payload for a requested object.

    Message must name the object so the diagnostic is object-specific
    (manifest v2 Section 7 failure invariant).
    """


class OutOfServedWindowError(AssemblerError):
    """The requested epoch lies outside the cache's served_window bound.

    Only raised once served_window is populated (a builder change tracked
    with F1). While served_window is null the resolver warns instead of
    raising, since it has no bound to enforce.
    """


class UnknownObjectError(AssemblerError):
    """A requested slug is not in the catalog / served cache."""

"""Type 1 classification - backwards-incompatible changes.

This is the one place an LLM is justified. Changelog text is unstructured prose
with no consistent marker for "this will break you" - "USE_L10N is removed" and
"the default value of X changed" are both breaking, phrased nothing alike, and
sit beside dozens of harmless entries. Keyword matching would be brittle in both
directions.

The model is asked for strict structured JSON (`breaking: bool`, `reason: str`)
so the output slots straight into a `Finding` with no free-text parsing, and so a
judge can see exactly what the model was and was not allowed to decide.

Filled in at Stage 5.
"""

from __future__ import annotations

from ..models import ChangelogEntry, Finding


def classify(entries: list[ChangelogEntry]) -> list[Finding]:
    """Ask Claude which releases carry breaking changes. (Stage 5)"""
    raise NotImplementedError("Implemented in Stage 5.")

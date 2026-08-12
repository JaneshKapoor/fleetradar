"""Type 2 classification - end-of-support cutoffs.

Deliberately model-free. An EOL verdict is a date comparison against
`EolEntry.eol_date`, and a date comparison is deterministic, instant, free, and
trivially explainable to a judge. Reaching for an LLM here would be worse on
every axis. The LLM is reserved for Stage 5's breaking-change pass, where the
input is genuinely unstructured prose.

Filled in at Stage 5.
"""

from __future__ import annotations

from datetime import date

from ..models import EolEntry, Finding


def classify(entries: list[EolEntry], as_of: date | None = None) -> list[Finding]:
    """Flag every version whose support window has closed. (Stage 5)

    `as_of` is injectable so tests can pin a date rather than depending on when
    the suite happens to run.
    """
    raise NotImplementedError("Implemented in Stage 5.")

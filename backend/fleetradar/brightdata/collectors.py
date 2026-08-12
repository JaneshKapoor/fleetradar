"""Programmatic triggering of the two Bright Data Scraper Studio collectors.

The collectors are *authored* interactively with the `bdata` CLI (Stages 2-3):

    bdata scraper create <url> "<extraction prompt>"   -> returns a collector_id
    bdata scraper run <collector_id>
    bdata scraper heal <collector_id> "<what broke>"   -> proposes a fix diff

Once a collector exists, its ID goes in `.env` and this module drives it through
the `brightdata-sdk` Python SDK. Shelling out to the CLI on every pipeline run
would work, but the SDK gives us real error handling and makes recurring runs a
scheduled function call instead of a subprocess.

Division of labour, restated because it is the core of the submission:
    Collector A  changelog / release pages  -> ChangelogEntry  -> Type 1 breaking
    Collector B  EOL / support pages        -> EolEntry        -> Type 2 EOL

Filled in at Stage 4.
"""

from __future__ import annotations

from ..models import ChangelogEntry, EolEntry


def run_collector_a() -> list[ChangelogEntry]:
    """Run Collector A over the watchlist's changelog URLs. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def run_collector_b() -> list[EolEntry]:
    """Run Collector B over the watchlist's EOL URLs. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")

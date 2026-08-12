"""Loader for `config/watchlist.json`.

Kept separate from `config.py` because the watchlist is project data (which
packages we track and where their pages live) rather than deployment config
(keys and paths). The collectors, the classifiers and the correlation engine all
read it through here so there is exactly one parse of that file.

Filled in at Stage 2, when Collector A first needs the changelog URLs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WatchedPackage:
    """One entry from the watchlist, resolved into a usable object."""

    id: str
    display_name: str
    ecosystem: str
    # Maps a package manager to the names that manager would report for this
    # package. This is the join key the correlation engine uses in Stage 6:
    # the agent reports "libssl3", the radar knows it as "openssl".
    match: dict[str, list[str]]
    version_granularity: str  # "major" | "minor" - how far to truncate before comparing
    changelog_url: str | None
    eol_url: str | None


def load() -> list[WatchedPackage]:
    """Parse the watchlist into `WatchedPackage` objects. (Stage 2)"""
    raise NotImplementedError("Implemented in Stage 2 alongside Collector A.")

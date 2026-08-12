"""SQLite persistence layer.

One module owns every SQL statement in the project. Everything else deals in the
pydantic models from `models.py` and never sees a cursor, which keeps the
swap-to-Postgres path (a post-hackathon goal) a single-file change.

Tables, in pipeline order:
    hosts        one row per fleet host, latest inventory wins
    packages     installed packages, keyed to a host
    changelogs   raw Collector A output
    eol          raw Collector B output
    findings     classifier verdicts (Stage 5)

Raw collector output is stored verbatim before classification runs. That
separation means a re-classification (say, a better breaking-change prompt) does
not require re-scraping, and it gives us the "example structured output" the
submission asks for straight out of the database.

Filled in at Stage 4, when the collectors first have data to persist.
"""

from __future__ import annotations

import sqlite3

from .models import ChangelogEntry, EolEntry, Finding, HostInventory


def connect() -> sqlite3.Connection:
    """Open the SQLite database, creating it if needed. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def init_schema(conn: sqlite3.Connection) -> None:
    """Create tables if they do not exist. Safe to call on every run. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


# --- Writes ----------------------------------------------------------------

def upsert_host_inventory(conn: sqlite3.Connection, inventory: HostInventory) -> None:
    """Replace a host's package list with its latest report. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def save_changelog_entries(conn: sqlite3.Connection, entries: list[ChangelogEntry]) -> None:
    """Persist raw Collector A output. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def save_eol_entries(conn: sqlite3.Connection, entries: list[EolEntry]) -> None:
    """Persist raw Collector B output. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def save_findings(conn: sqlite3.Connection, findings: list[Finding]) -> None:
    """Persist classifier verdicts. (Stage 5)"""
    raise NotImplementedError("Implemented in Stage 5.")


# --- Reads -----------------------------------------------------------------

def all_hosts(conn: sqlite3.Connection) -> list[HostInventory]:
    """Every host's current inventory, for the correlation engine. (Stage 4)"""
    raise NotImplementedError("Implemented in Stage 4.")


def all_findings(conn: sqlite3.Connection) -> list[Finding]:
    """Every classifier verdict, for the correlation engine. (Stage 5)"""
    raise NotImplementedError("Implemented in Stage 5.")

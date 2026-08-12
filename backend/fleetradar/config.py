"""Runtime configuration, loaded from the environment (see `.env.example`).

Nothing here reads a secret at import time beyond `os.environ`, so importing this
module is safe in tests and in CI where no keys are set. Callers that genuinely
need a key call `require()` and get a clear error instead of a `None` that blows
up three layers deeper.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Repo root = two levels up from backend/fleetradar/config.py
REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")

# --- Paths -----------------------------------------------------------------

WATCHLIST_PATH = REPO_ROOT / "config" / "watchlist.json"

DB_PATH = Path(
    os.environ.get("FLEETRADAR_DB_PATH", "data/fleetradar.db")
)
if not DB_PATH.is_absolute():
    DB_PATH = REPO_ROOT / DB_PATH

# Where the Stage 8 snapshot export writes the joined radar for the dashboard.
SNAPSHOT_PATH = REPO_ROOT / "frontend" / "public" / "radar.json"

# --- Credentials -----------------------------------------------------------

# Collector IDs are not env config - they are per-source and live in
# config/watchlist.json. See the note in .env.example.
BRIGHTDATA_API_KEY = os.environ.get("BRIGHTDATA_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def require(name: str) -> str:
    """Return an env var's value, or fail loudly naming what to set.

    Used at the point of use rather than at import, so a missing Anthropic key
    never blocks a run that only touches the EOL path.
    """
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return value

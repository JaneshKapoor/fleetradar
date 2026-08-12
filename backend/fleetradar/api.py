"""FastAPI app - the ingest endpoint the fleet agent talks to.

Deliberately thin. The API's only job is to accept inventories from hosts and
expose the joined radar for inspection; the scraping, classification and
correlation all run as pipeline steps (see `pipeline.py`), not inside a request.

Run locally with:
    uvicorn fleetradar.api:app --reload    # from backend/

Interactive docs at http://localhost:8000/docs - the pydantic models in
`models.py` generate that page, which is worth showing in the demo video.

Filled in at Stage 7, alongside the agent that POSTs to it.
"""

from __future__ import annotations

from fastapi import FastAPI

from .models import HostInventory, RadarEntry

app = FastAPI(
    title="Fleet Radar",
    description="Fleet package inventory ingest and exposure radar.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check - lets the agent verify the backend before POSTing."""
    return {"status": "ok"}


@app.post("/inventory")
def ingest_inventory(inventory: HostInventory) -> dict[str, object]:
    """Accept one host's package inventory. (Stage 7)

    FastAPI validates the body against `HostInventory` before this runs, so a
    malformed agent report is rejected with a 422 rather than corrupting the DB.
    """
    raise NotImplementedError("Implemented in Stage 7.")


@app.get("/radar")
def get_radar() -> list[RadarEntry]:
    """The joined per-host exposure view. (Stage 6)"""
    raise NotImplementedError("Implemented in Stage 6.")

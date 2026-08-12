"""Command-line entry point for the Fleet Radar agent.

    fleetradar-agent --backend http://radar.internal:8000
    fleetradar-agent --dry-run          # print the inventory, POST nothing

`--dry-run` exists so an operator can see exactly what would leave their machine
before it does. That matters for adoption: this reads a full software inventory
off production hosts, and "show me first" is a fair thing to ask.

Uses `urllib.request` rather than `requests` to keep the agent dependency-free -
see the design note in `collect.py`.

Filled in at Stage 7.
"""

from __future__ import annotations


def main() -> int:
    """Parse args, build the inventory, POST it to the backend. (Stage 7)"""
    raise NotImplementedError("Implemented in Stage 7.")

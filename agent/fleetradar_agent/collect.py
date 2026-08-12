"""Reads what is installed on the local host.

Runs on any Linux host - bare metal, VM, cloud instance or container - because
they all expose the same package-manager interface. The agent only ever reads:
it never installs, upgrades or modifies anything.

Detection order:
    1. `/etc/os-release`  -> distro id + version  ("ubuntu-22.04")
    2. distro family      -> which manager to query
         debian family  -> `dpkg -l`
         rhel family    -> `rpm -qa`
    3. `uname -r`         -> kernel version

DESIGN NOTE - stdlib only. This module deliberately imports nothing outside the
Python standard library and does not share code with the backend, even though
both speak the same JSON shape. The agent has to install cleanly on arbitrary
fleet hosts, some running old system Pythons; making it depend on pydantic or on
the backend package would turn "install the agent" into a dependency problem on
every server. The contract is enforced on the receiving end instead, where
FastAPI validates the POST body against `HostInventory` and 422s anything
malformed. The authoritative schema lives in `backend/fleetradar/models.py`.

Filled in at Stage 7.
"""

from __future__ import annotations


def detect_distro() -> str:
    """Parse `/etc/os-release` into an 'ubuntu-22.04' style identifier. (Stage 7)"""
    raise NotImplementedError("Implemented in Stage 7.")


def detect_kernel() -> str:
    """Return `uname -r`. (Stage 7)"""
    raise NotImplementedError("Implemented in Stage 7.")


def read_packages(distro: str) -> list[dict[str, str]]:
    """Query the right package manager for the detected distro family. (Stage 7)

    Returns dicts of {"name", "version", "manager"} - the `packages` array of the
    inventory payload.
    """
    raise NotImplementedError("Implemented in Stage 7.")


def build_inventory() -> dict[str, object]:
    """Assemble the full inventory payload for this host. (Stage 7)

    Shape (validated backend-side against `HostInventory`):
        {"hostname": str, "distro": str, "kernel": str, "packages": [...]}
    """
    raise NotImplementedError("Implemented in Stage 7.")

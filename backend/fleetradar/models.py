"""Data contracts for the whole system.

Every JSON payload that crosses a boundary in Fleet Radar is defined here, once.
The agent, the collectors, the classifiers, the correlation engine and the
dashboard export all speak these shapes, so a change to a field is a change in
exactly one file.

Pipeline order (mirrors the build order in the README):

    HostInventory      agent  ->  backend        (what is installed, per host)
    ChangelogEntry     Collector A raw output    (releases + changelog text)
    EolEntry           Collector B raw output    (version + end-of-support date)
    Finding            classifier output         (a verdict about one version)
    RadarEntry         correlation output        (a verdict about one host)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

# A package manager the local agent can read. Extended when we add more distros.
PackageManager = Literal["apt", "rpm", "npm", "pip"]

# The two signal types the radar detects, per the project brief.
#   "breaking" - a newer release introduces a backwards-incompatible change
#   "eol"      - the installed version is past its official end-of-support date
FlagType = Literal["breaking", "eol"]


# --------------------------------------------------------------------------
# Stage 7 - what the local agent reports
# --------------------------------------------------------------------------

class InstalledPackage(BaseModel):
    """One package as the host's package manager reports it."""

    name: str
    version: str
    manager: PackageManager


class HostInventory(BaseModel):
    """A full inventory POSTed by one fleet host to `POST /inventory`.

    Works identically on bare metal, VMs, cloud instances and containers -
    they all expose the same package-manager interface.
    """

    hostname: str
    distro: str = Field(description="Normalised from /etc/os-release, e.g. 'ubuntu-22.04'.")
    kernel: str = Field(description="Output of `uname -r`, e.g. '5.15.0'.")
    packages: list[InstalledPackage]

    # Set by the backend on ingest, not by the agent, so hosts need no clock sync.
    reported_at: datetime | None = None


# --------------------------------------------------------------------------
# Stages 2-3 - raw output from the Bright Data collectors
# --------------------------------------------------------------------------

class ChangelogEntry(BaseModel):
    """One release, as extracted by Collector A from a changelog/release page.

    `changelog_text` is kept raw and unparsed on purpose: the breaking-change
    classifier in Stage 5 reads the prose, so trimming it here would throw away
    the exact signal we need.
    """

    package: str = Field(description="watchlist `id`, not the OS package name.")
    version: str
    release_date: date | None = None
    changelog_text: str

    source_url: str | None = None
    scraped_at: datetime | None = None


class EolEntry(BaseModel):
    """One version's support window, as extracted by Collector B."""

    package: str = Field(description="watchlist `id`, not the OS package name.")
    version: str
    eol_date: date | None = Field(
        default=None,
        description="None means the page lists the version as still supported.",
    )

    source_url: str | None = None
    scraped_at: datetime | None = None


# --------------------------------------------------------------------------
# Stage 5 - classifier output (one verdict about one package version)
# --------------------------------------------------------------------------

class Finding(BaseModel):
    """A single classified signal, independent of any host.

    EOL findings come from plain date arithmetic; breaking findings come from an
    LLM pass over `ChangelogEntry.changelog_text`. Both land in this one shape so
    the correlation engine does not care which produced them.
    """

    package: str
    version: str
    flag: FlagType
    detail: str = Field(description="Human-readable justification shown in the dashboard.")

    # Only set for `flag="breaking"`, so we can show the evidence behind a verdict.
    source_url: str | None = None


# --------------------------------------------------------------------------
# Stage 6 - correlation output (what the dashboard renders)
# --------------------------------------------------------------------------

class RadarFlag(BaseModel):
    """A finding as attached to a specific host."""

    type: FlagType
    detail: str


class RadarEntry(BaseModel):
    """One row of the dashboard: a host, a package, and why it is exposed."""

    hostname: str
    package: str
    installed_version: str
    current_stable: str | None = None
    flags: list[RadarFlag]

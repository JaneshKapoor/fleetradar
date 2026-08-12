"""The correlation engine - joins fleet inventory against classified findings.

This is where Fleet Radar earns its name. The collectors know facts about the
world ("Python 3.7 went EOL on 2023-06-27"); the agent knows facts about your
fleet ("web-01 has python3 3.7.0 installed"). Neither is actionable alone. This
module produces the sentence a sysadmin can act on:

    web-01 is running an unsupported Python.

Two non-obvious parts, both handled here rather than in the classifier:

1. Name matching. The agent reports OS package names ("libssl3", "python3-django")
   which rarely equal the name the upstream project uses. `watchlist.match` maps
   them, so this join is a lookup rather than fuzzy string work.

2. Version matching. Support windows are published per release line, not per
   patch. A host on 3.7.9 is covered by the 3.7 EOL date, so both sides get
   truncated to the package's `version_granularity` before comparing.

Filled in at Stage 6.
"""

from __future__ import annotations

from .models import Finding, HostInventory, RadarEntry


def correlate(
    hosts: list[HostInventory],
    findings: list[Finding],
) -> list[RadarEntry]:
    """Join every host's packages against every finding. (Stage 6)"""
    raise NotImplementedError("Implemented in Stage 6.")

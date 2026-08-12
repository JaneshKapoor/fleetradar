"""Loader for `config/watchlist.json`.

Kept separate from `config.py` because the watchlist is project data (which
packages we track and where their pages live) rather than deployment config
(keys and paths). The collectors, the classifiers and the correlation engine all
read it through here so there is exactly one parse of that file.

The loader's real job is expanding templated changelog sources. Release notes are
published one page per release line, so a source declares a `url_template` and
the `versions` to expand it over:

    "https://docs.djangoproject.com/en/stable/releases/{version}/"  +  ["4.2", "5.1", "5.2"]
        -> three URLs, one structure, one scraper, one `--urls` batch

Run `python -m fleetradar.watchlist` to print the full expansion.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .config import WATCHLIST_PATH

# Granularities a package may declare, mapped to how many dot-separated
# components of a version string identify its release line.
_GRANULARITY_COMPONENTS = {"major": 1, "minor": 2}


@dataclass(frozen=True)
class Source:
    """One scrape target: a set of URLs sharing a single page structure.

    All URLs in a `Source` come from the same template, so one Bright Data
    scraper handles all of them and `collector_id` is a property of the source
    rather than of any individual URL.
    """

    urls: tuple[str, ...]
    structure: str
    collector_id: str | None = None

    @property
    def is_built(self) -> bool:
        """True once `bdata scraper create` has been run for this source."""
        return self.collector_id is not None


@dataclass(frozen=True)
class WatchedPackage:
    """One entry from the watchlist, resolved into a usable object."""

    id: str
    display_name: str
    ecosystem: str

    # Maps a package manager to the names that manager would report for this
    # package. This is the join key the correlation engine uses in Stage 6:
    # the agent reports "libssl3", the radar knows it as "openssl".
    match: dict[str, list[str]] = field(repr=False)

    # "major" or "minor" - how far to truncate a version before comparing.
    # Support windows are published per release line, not per patch.
    version_granularity: str

    changelog: Source
    # None for packages with no published support calendar (e.g. express).
    eol: Source | None

    def matches(self, package_name: str, manager: str) -> bool:
        """True if an installed package reported by `manager` is this package.

        Case-insensitive because PyPI reports "Django" while apt reports
        "python3-django".
        """
        candidates = self.match.get(manager, [])
        return package_name.lower() in {c.lower() for c in candidates}

    def release_line(self, version: str) -> str:
        """Truncate a version to this package's tracked release line.

        Python is tracked per minor line, so 3.7.9 -> "3.7". Node is tracked per
        major line, so 18.19.1 -> "18". Both sides of an EOL comparison get
        truncated this way before matching.
        """
        return truncate_version(version, self.version_granularity)


def truncate_version(version: str, granularity: str) -> str:
    """Cut a version string down to `granularity` components.

    Tolerates the noise real package managers emit - epochs ("1:3.7.9"), distro
    suffixes ("1.1.1f-1ubuntu2.16"), and leading "v" - because this runs against
    whatever `dpkg -l` reports, not against clean semver.
    """
    try:
        components = _GRANULARITY_COMPONENTS[granularity]
    except KeyError:
        raise ValueError(
            f"unknown version_granularity {granularity!r}; "
            f"expected one of {sorted(_GRANULARITY_COMPONENTS)}"
        ) from None

    cleaned = version.strip().lstrip("vV")

    # Drop a Debian epoch prefix ("1:3.7.9" -> "3.7.9").
    if ":" in cleaned:
        cleaned = cleaned.split(":", 1)[1]

    # Drop any distro revision or pre-release suffix ("1.1.1f-1ubuntu2" -> "1.1.1f").
    for separator in ("-", "+", "~"):
        cleaned = cleaned.split(separator, 1)[0]

    return ".".join(cleaned.split(".")[:components])


def _parse_source(raw: dict | None) -> Source | None:
    """Build a `Source`, expanding a url_template over its versions if present.

    Handles both source shapes: templated (one page per release line, the common
    case) and single-URL (express's GitHub releases feed, and every EOL source,
    since support calendars publish one table covering all versions).
    """
    if raw is None:
        return None

    if "url_template" in raw:
        template = raw["url_template"]
        versions = raw["versions"]
        if not versions:
            raise ValueError(f"url_template {template!r} has no versions to expand")
        urls = tuple(template.format(version=v) for v in versions)
    else:
        urls = (raw["url"],)

    return Source(
        urls=urls,
        structure=raw.get("structure", ""),
        collector_id=raw.get("collector_id"),
    )


def load() -> list[WatchedPackage]:
    """Parse the watchlist into `WatchedPackage` objects."""
    with open(WATCHLIST_PATH, encoding="utf-8") as handle:
        raw = json.load(handle)

    packages = []
    for entry in raw["packages"]:
        changelog = _parse_source(entry["sources"]["changelog"])
        if changelog is None:
            raise ValueError(f"package {entry['id']!r} has no changelog source")

        packages.append(
            WatchedPackage(
                id=entry["id"],
                display_name=entry["display_name"],
                ecosystem=entry["ecosystem"],
                match=entry["match"],
                version_granularity=entry["version_granularity"],
                changelog=changelog,
                eol=_parse_source(entry["sources"]["eol"]),
            )
        )
    return packages


def by_id() -> dict[str, WatchedPackage]:
    """The watchlist keyed by package id, for lookups during correlation."""
    return {p.id: p for p in load()}


def _main() -> None:
    """Print the expanded watchlist - a quick check that templates resolve."""
    total = 0
    for package in load():
        built = "built" if package.changelog.is_built else "not built"
        print(f"\n{package.display_name}  ({package.id}, per-{package.version_granularity} line)")
        print(f"  changelog [{built}] - {package.changelog.structure[:70]}")
        for url in package.changelog.urls:
            print(f"      {url}")
            total += 1
        if package.eol is None:
            print("  eol       - none published")
        else:
            built = "built" if package.eol.is_built else "not built"
            print(f"  eol       [{built}]")
            for url in package.eol.urls:
                print(f"      {url}")
                total += 1
    print(f"\n{total} URLs across {len(load())} packages")


if __name__ == "__main__":
    _main()

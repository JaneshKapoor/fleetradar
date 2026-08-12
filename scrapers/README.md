# Scrapers

Everything about the two Bright Data Scraper Studio collectors: the exact
extraction prompts they were created with, their collector IDs, and sample raw
output committed as evidence.

| Directory | Collector | Feeds |
|---|---|---|
| `collector-a-changelog/` | A — changelog / release pages | Type 1, breaking-change detection |
| `collector-b-eol/` | B — EOL / support pages | Type 2, support-cutoff detection |

Each collector directory holds:

- `README.md` — target URLs, the extraction prompt, the collector ID, and any
  per-source adjustments
- `samples/` — real raw output, trimmed to a readable size, committed so the
  extraction shape is reviewable without running anything

The narrative write-up for the submission lives in
[`../docs/SCRAPER_STUDIO.md`](../docs/SCRAPER_STUDIO.md); these directories hold
the artefacts it refers to.

Populated in Stages 2 and 3.

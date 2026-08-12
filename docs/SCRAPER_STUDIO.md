# How Fleet Radar uses Bright Data Scraper Studio

This is the submission write-up required by the hackathon rules. It is filled in
as Stages 2, 3, 4 and 9 land, rather than reconstructed afterwards.

> 🚧 **Status: Stage 1 (scaffold) complete.** Collector authoring begins at Stage 2.

---

## Summary

Fleet Radar uses **two custom collectors authored in Scraper Studio**. Neither is
taken from the Bright Data Scrapers Library — both are created from scratch with
`bdata scraper create` against pages that no off-the-shelf scraper covers.

| | Collector A | Collector B |
|---|---|---|
| **Targets** | Changelog / release pages | EOL / support pages |
| **Extracts** | version, release date, full changelog text | version, end-of-support date |
| **Feeds** | Type 1 — breaking-change detection | Type 2 — support-cutoff detection |
| **Collector ID** | _(filled in at Stage 2)_ | _(filled in at Stage 3)_ |

## Why this needs a scraper at all

The data Fleet Radar depends on — which versions of which packages are still
supported, and which releases broke something — is published exclusively as
human-readable web pages. There is no comprehensive API. Vendors publish it as:

- a documentation status table (Python's developer guide)
- a vendor download page with a supported-versions block (Django)
- a blog-style chronological release feed (Node.js)
- a GitHub releases page (Express)
- a dense plain-text changelog file (OpenSSL)

Five sources, five structures, one required output shape. That is the problem
Scraper Studio solves here, and it is why the watchlist was chosen for structural
diversity rather than convenience.

## Collector A — changelog / release pages

_To be written in Stage 2: target URLs, the exact extraction prompt passed to
`bdata scraper create`, the returned collector ID, sample output, and what had to
be adjusted per source._

```bash
bdata scraper create <url> "Extract version, release date, and full changelog text for each release"
```

## Collector B — EOL / support pages

_To be written in Stage 3._

```bash
bdata scraper create <url> "Extract version number and end-of-support date for each release"
```

## Programmatic runs via the Python SDK

_To be written in Stage 4._

Collectors are authored interactively with the `bdata` CLI, then driven from the
backend through `brightdata-sdk` so recurring runs are a scheduled function call
rather than a subprocess. Code: `backend/fleetradar/brightdata/collectors.py`.

## Self-healing

_To be written in Stage 9 — the demo centrepiece._

When a target page's layout changes, the collector's extraction breaks. Rather
than hand-patching selectors, `bdata scraper heal` is given a description of what
went wrong and what correct output looks like; it proposes a diff and stops at a
human approval gate.

```bash
bdata scraper heal <collector_id> "<what's wrong and what correct output should look like>"
```

This section will document: which collector broke, how we detected it, the exact
heal prompt, the proposed diff, and the verified output after approval.

**Why human-in-the-loop matters here:** Fleet Radar's output drives patching
decisions on production servers. A scraper that silently "fixes" itself into
extracting the wrong column would produce confidently wrong EOL dates, which is
worse than no data at all. The approval gate is a deliberate design choice, not a
default we left on.

## Reliability notes

_To be written across Stages 2–4: retry behaviour, partial-failure handling, and
how the pipeline degrades when one source is unreachable._

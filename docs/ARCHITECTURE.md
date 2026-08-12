# Architecture

Why Fleet Radar is shaped the way it is. Written as decisions are made, so the
team can defend every one of them — a hackathon rule, not just good practice.

---

## The central idea

Fleet Radar exists because two facts that are individually useless become
actionable when joined:

| Fact | Where it lives | Alone, it tells you |
|---|---|---|
| `web-01` has `python3` 3.7.0 installed | on the server | nothing — 3.7.0 sounds fine |
| Python 3.7 lost support on 2023-06-27 | on a vendor page | nothing — you don't know if you run it |

Joined: **`web-01` is running an unsupported Python.** That join is the product.
Everything else in this repo is plumbing that gets the two facts into the same
process.

## Component boundaries

### Local agent → backend (HTTP POST)

The agent is a **separate installable package with zero dependencies**, and it
shares no code with the backend even though both speak the same JSON shape.

*Why:* the agent has to install on arbitrary fleet hosts, some running old system
Pythons. Every dependency is another host where `pip install` fails. Sharing the
backend's pydantic models would drag FastAPI's dependency tree onto production
servers to validate a four-field payload.

*Cost:* the schema is written twice — as pydantic models in
`backend/fleetradar/models.py` (authoritative) and as documented dict shapes in
the agent. We accept that, and enforce the contract at the boundary: FastAPI
validates every POST and rejects malformed reports with a 422 rather than letting
them corrupt the database.

The agent is **read-only**. It runs `dpkg -l` / `rpm -qa` / `uname -r` and posts
names and versions. It never installs, upgrades, or reads file contents.
`--dry-run` prints the exact payload without sending it.

### Bright Data pipeline → backend (independent)

The scraping pipeline knows nothing about the fleet, and the fleet knows nothing
about the scrapers. They meet only in the correlation engine.

*Why:* the two run on completely different clocks. Fleet inventory changes when
someone patches a server; vendor EOL pages change a few times a year. Coupling
them would mean re-scraping the whole watchlist every time a host checks in.
Kept independent, each side runs on its own schedule and the correlation is a
cheap in-memory join over whatever the latest of each is.

### Raw storage before classification

Collector output is persisted **verbatim** before any classification runs.

*Why:* re-classifying is cheap, re-scraping is not. When we improve the
breaking-change prompt in Stage 5 we re-run the classifier over stored raw text
instead of hitting every vendor page again. It also gives us the "example
structured output" the submission requires straight out of the database, and it
means a bad LLM response can never destroy the underlying evidence.

## Key decisions

### Why an LLM for Type 1 but not Type 2

**Type 2 (EOL) is a date comparison.** `installed_version`'s release line has an
`eol_date`; is it in the past? Deterministic, instant, free, and explainable to a
judge in one sentence. Using a model here would be slower, costlier, and less
reliable than `<`.

**Type 1 (breaking change) is prose comprehension.** "USE_L10N is removed" and
"the default value of `X` changed to `Y`" are both breaking, share no keywords,
and sit among dozens of harmless entries in the same changelog. Keyword matching
fails in both directions — it misses rephrased breakage and fires on
"fixed a breaking bug". This is exactly what a language model is for.

The model is constrained to structured JSON (`breaking: bool`, `reason: str`) so
its output drops straight into a `Finding` with no free-text parsing, and so the
boundary of what it is allowed to decide is visible in the code.

### Why `config/watchlist.json`

Three components need to agree on what we watch: the collectors need URLs, the
classifier needs package identities, and the correlation engine needs the mapping
from upstream names to OS package names. One file, parsed once in
`backend/fleetradar/watchlist.py`, instead of three hardcoded lists that drift.

The `match` field is doing real work: `dpkg` reports `libssl3` and
`python3-django`, which equal neither `openssl` nor `django`. Without an explicit
mapping the join degenerates into fuzzy string matching, which is exactly the
kind of thing that silently misses the one exposed host that mattered.

### Why "Collector A" is five scrapers, not one

`bdata scraper create` builds a scraper from **one** example URL, and
`bdata scraper run <id> --urls a,b,c` then runs it over many. The natural unit is
therefore *one scraper per page structure*, batched over every URL sharing that
structure — not one scraper per signal type.

Our five changelog sources are structurally unrelated: Sphinx documentation
(Python, Django), a vendor blog post (Node), a vendor release-notes page
(OpenSSL), and a GitHub releases feed (Express). A scraper generated against
Django's docs cannot read Node's blog. So "Collector A" is a *family* of five
scrapers sharing one output contract (`ChangelogEntry`), and "Collector B" is a
family of four sharing `EolEntry`.

This is better for the submission, not just more correct: self-healing gets
demonstrated per structure, and each scraper is small enough to explain.

Consequence: collector IDs are per-source, so they live in
`config/watchlist.json` rather than as two env vars.

### Why changelog sources are templated per release line

Release notes are published one page per version
(`.../releases/5.2/`, `.../releases/5.1/`). A changelog source is therefore a
`url_template` plus the `versions` to expand it over, and that expansion is
exactly the URL list handed to `--urls`. EOL sources need no template — support
calendars are published as a single table covering every version.

Express is the one exception: all its releases render on a single GitHub page, so
it declares a plain `url`. The loader has to handle both.

### Why content pages, not index pages

Schema v1 of the watchlist pointed at pages like
`docs.djangoproject.com/en/stable/releases/`. That page is a **list of links** —
it has versions and dates but no release-note prose. Since changelog prose is the
entire input to Type 1 detection, a scraper built against it would have populated
`version` and `release_date` correctly, returned an empty `changelog_text`, and
produced a classifier that confidently found zero breaking changes.

Every URL in the watchlist was fetched and confirmed to contain real
breaking-change text before being committed. Two lessons worth keeping:

- **A scraper that returns well-formed rows is not a working scraper.** Validate
  the *content* of the field the pipeline actually consumes.
- **GitHub blob pages lazy-load file content via JS** and return ~3k chars of
  shell to a plain fetch, while GitHub *releases* pages render server-side. That
  ruled out `CHANGELOG_V22.md` and `CHANGES.md` as targets.

### Why version granularity is per-package

Support windows are published per release *line*, not per patch. A host on Python
3.7.9 is covered by the 3.7 EOL date; a host on Node 18.19.1 is covered by the
Node 18 schedule. Different projects draw that line at different levels, so each
watchlist entry declares its own `version_granularity` (`major` or `minor`) and
both sides get truncated to it before comparison.

### Why SQLite + a JSON snapshot, not a hosted database

The dashboard is served from Vercel as static data exported from SQLite by a
build step.

*Why:* the demo cannot fail on stage. No free-tier cold start, no connection
limits, no live database to be down during judging. The data is still entirely
real — genuinely scraped, genuinely correlated — it is just materialised at build
time instead of query time.

*Cost:* refreshing the dashboard means re-running the pipeline and redeploying,
so it is not live-updating. For a fleet-audit tool whose inputs change on a
weekly cadence, that is an acceptable trade; a hosted Postgres is a documented
post-hackathon path, and the storage layer is isolated in `storage.py`
specifically so that swap is a one-file change.

### Why FastAPI

Pydantic models give validated request bodies for free, and those same models are
the documented data contracts in `models.py` — one definition serving both jobs.
The auto-generated `/docs` page is also a genuinely useful artefact for the demo
video.

---

## Open questions

Tracked here as they come up, resolved as stages land.

- **Collector A output volume.** Confirmed real: Python's "What's New" pages run
  ~115k characters each, against ~9k for OpenSSL. Whole-page text would be
  wasteful to store and expensive to classify. Mitigation is to bound extraction
  to the breaking-change sections, and the watchlist currently tracks three
  release lines per package rather than every release. *Resolve in Stage 2 by
  scoping the extraction prompt.*
- **Express EOL.** No formal end-of-support calendar exists, so `express` carries
  a changelog signal only. The pipeline must tolerate a `null` EOL source rather
  than assume every package has one. *Resolve in Stage 3.*
- **OpenSSL changed its versioning scheme at 3.0, and one granularity cannot
  express both.** Pre-3.0 releases are `MAJOR.MINOR.FIX` plus a letter
  (`1.1.1f`), where the support line is the *three*-component `1.1.1`. From 3.0
  the scheme is ordinary `MAJOR.MINOR.PATCH`, where the line is the
  *two*-component `3.0`. Declaring `minor` truncates `1.1.1f` to `1.1`, which
  matches no line endoflife.date publishes. This matters because `1.1.1f` is the
  stock OpenSSL on Ubuntu 20.04 and is very likely to appear in the demo fleet.
  Adding a `patch` granularity does not fix it — that would break 3.x instead.
  The likely answer is to match an installed version against the version strings
  Collector B actually returned, by longest prefix, rather than truncating to a
  fixed depth. *Resolve in Stage 6.*
- **Which versions to track.** The watchlist pins three release lines per
  package. For breaking-change detection to be useful, the tracked set has to
  cover the releases *newer than* what the fleet actually runs, so this may need
  widening once the demo fleet's inventory is fixed. *Resolve in Stage 6.*
- **Kernel version.** The agent collects `uname -r`, but the kernel is not yet on
  the watchlist and has a different support model than userspace packages.
  *Resolve in Stage 6 or defer.*

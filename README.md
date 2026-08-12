# Fleet Radar

**Know which of your servers are running software that is unsupported or about to break — before it breaks.**

Built for [Into the Scrape-Verse](https://wemakedevs.org) (WeMakeDevs × Bright Data, Aug 17–23 2026).

> 🚧 **Status: in development.** This README is filled in stage by stage as the
> build progresses. See [Build status](#build-status) for what works today.

---

## The problem

Every organisation running Linux servers has the same blind spot. Somewhere in
the fleet is a box running an OpenSSL that stopped receiving security patches
eighteen months ago, or a Python that went end-of-life two releases back. Nobody
knows which box, because the two halves of that answer live in different places:

- **What's installed** is on the servers, scattered across dozens of hosts.
- **What's still supported** is on the web, scattered across vendor changelogs,
  release-notes pages and EOL calendars — each with its own layout, none with a
  usable API.

Fleet Radar joins those two halves.

## What it does

A read-only local agent inventories installed packages on every host. A Bright
Data Scraper Studio pipeline scrapes the vendor pages that say what's supported.
A correlation engine joins them and answers the question a sysadmin actually
has: *which of my servers are exposed, and why?*

**Two signal types:**

| Type | Signal | How it's detected |
|---|---|---|
| **1** | **Breaking change** — a newer release introduces a backwards-incompatible change | LLM pass over scraped changelog prose |
| **2** | **EOL / support cutoff** — the installed version is past its official end-of-support date | Plain date comparison against scraped EOL tables |

## Architecture

```
Any Linux host (bare metal / VM / cloud instance / container)
  └─ Local agent: detects distro, reads installed packages, reports inventory
        │
        ▼
Central backend (Python + FastAPI)
  └─ Aggregates fleet inventory from all hosts  →  SQLite
        │
        ▼
Correlation engine
  ├─ Fleet inventory (from backend)
  └─ Package radar (from Bright Data pipeline, below) ──┐
        │                                                │
        ▼                                                │
Fleet dashboard (Next.js) — per-server exposure view      │
                                                          │
Bright Data pipeline (independent, feeds the correlation) ◄┘
  ├─ Collector A: release/changelog pages → breaking-change detection (Type 1)
  └─ Collector B: EOL/support pages       → support-cutoff detection (Type 2)
```

Full reasoning behind each boundary: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## How Bright Data Scraper Studio is used

Two **custom** collectors, authored in Scraper Studio — not pulled from the
Scrapers Library. They target deliberately heterogeneous page structures
(official docs tables, a vendor download page, a blog-style release feed, a
GitHub releases page, a dense plain-text changelog), which is what makes the
self-healing story real rather than staged.

Full write-up, including the self-heal demo: [`docs/SCRAPER_STUDIO.md`](docs/SCRAPER_STUDIO.md).

## Repository layout

| Path | What's in it |
|---|---|
| `config/watchlist.json` | Single source of truth: which packages we watch and which pages describe them |
| `agent/` | Dependency-free, read-only local agent (pip-installable CLI) |
| `backend/` | FastAPI ingest, Bright Data triggering, classification, correlation |
| `scrapers/` | Collector definitions, extraction prompts, sample raw output |
| `frontend/` | Next.js dashboard |
| `data/examples/` | Example structured output at each pipeline stage |
| `docs/` | Architecture and Scraper Studio write-ups |

## Build status

| # | Stage | Status |
|---|---|---|
| 1 | Repo scaffold | ✅ done |
| 2 | Collector A — changelog / release pages | ⬜ next |
| 3 | Collector B — EOL / support pages | ⬜ |
| 4 | `brightdata-sdk` wired into the backend, raw JSON persisted | ⬜ |
| 5 | Classification (EOL date logic + Claude breaking-change pass) | ⬜ |
| 6 | Correlation engine | ⬜ |
| 7 | Local agent | ⬜ |
| 8 | Next.js dashboard, deployed to Vercel | ⬜ |
| 9 | Staged self-heal demo | ⬜ |
| 10 | README, demo video, submission write-up | ⬜ |

## Getting started

```bash
git clone https://github.com/JaneshKapoor/fleetradar.git
cd fleetradar

python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

cp .env.example .env   # then fill in your keys
```

## Data ethics

Fleet Radar reads **only publicly available web data** — vendor changelogs,
release-notes pages and EOL calendars that anyone can open in a browser. No
login-protected, paywalled or private sources. The local agent is read-only and
reports package names and versions; it never reads file contents, credentials or
user data, and `--dry-run` shows an operator exactly what would be sent.

## AI assistance disclosure

This project was built with AI coding assistance (Claude Code). Every
architectural decision, scraper design and data-flow choice was made and is
explainable by the team — see `docs/ARCHITECTURE.md`, where the reasoning behind
each one is written down rather than assumed.

## License

MIT — see [`LICENSE`](LICENSE).

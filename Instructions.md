# Fleet Radar — project brief for Claude Code

Paste this whole document as your opening prompt to Claude Code (works with any current model — Opus 4.8, Sonnet 5, etc.). It has enough context to scaffold and build incrementally without you re-explaining the architecture each session.

## Context

Building for **Into the Scrape-Verse**, a hackathon by WeMakeDevs x Bright Data (Aug 17–23, 2026). Team of 2–4. Targeting the **Web-Slinger grand prize** (Best Use of Bright Data track — NVIDIA DGX Spark or $5,000).

Judging is on six equally-weighted criteria: potential impact, creativity, technical excellence, depth of Scraper Studio use, reliability/self-healing, and presentation quality.

**Hard requirements from the official rules — do not violate these:**
- Must use Bright Data Scraper Studio to create and run a **custom** scraper. Using only an existing scraper from the Bright Data Scrapers Library does not qualify.
- Must use only publicly available web data — no login-protected, paywalled, or private data.
- Final submission needs: a public repo, a clear README, example structured output, a demo video, and a clear explanation of how Scraper Studio was used.
- AI coding assistant use is allowed but must be disclosed in the submission.
- The team must be able to explain the scraper, architecture, and every technical decision — don't generate anything nobody on the team understands.

## What we're building: Fleet Radar

**One-line pitch:** a local agent inventories installed packages across an organization's Linux fleet (bare metal, VMs, cloud instances, containers — same agent works on all of them since they all expose the same package-manager interface); a Bright Data Scraper Studio pipeline scrapes changelog/release pages and EOL/support pages for those packages; a correlation engine joins the two to tell you, per server, exactly what's outdated, unsupported, or about to break.

**Two signal types the radar detects:**
- **Type 1 — breaking change:** a new release of a package introduces a backwards-incompatible change relevant to the installed version.
- **Type 2 — EOL / support cutoff:** the installed version has passed its official end-of-support date, independent of any specific new release.

## Architecture

```
Any Linux host (bare metal / VM / cloud instance / container)
  └─ Local agent: detects distro, reads installed packages, reports inventory
        │
        ▼
Central backend (Python)
  └─ Aggregates fleet inventory from all hosts
        │
        ▼
Correlation engine
  ├─ Fleet inventory (from backend)
  └─ Package radar (from Bright Data pipeline, below) ──┐
        │                                                 │
        ▼                                                 │
Fleet dashboard (Next.js) — per-server exposure view       │
                                                             │
Bright Data pipeline (independent, feeds the correlation) ◄┘
  ├─ Collector A: release/changelog pages → breaking-change detection (Type 1)
  └─ Collector B: EOL/support pages → support-cutoff detection (Type 2)
```

## Tech stack

- **Agent:** Python or Bash. Detect distro via `/etc/os-release`. Run `dpkg -l` (Debian/Ubuntu family) or `rpm -qa` (RHEL/Fedora/CentOS family). Grab `uname -r` for kernel version. POST inventory JSON to the backend. For the hackathon, ship as a pip-installable CLI or a `curl | sh` installer — a real `.deb`/`.rpm` is stated as a post-hackathon goal, not required for the demo.
- **Scraping — Bright Data CLI:**
  ```bash
  npm install -g @brightdata/cli
  bdata login

  # Collector A — changelog/release pages
  bdata scraper create <url> "Extract version, release date, and full changelog text for each release"
  # → returns a collector_id, reused with: bdata scraper run <collector_id>

  # Collector B — EOL/support pages
  bdata scraper create <url> "Extract version number and end-of-support date for each release"

  # Self-heal when a target page's layout changes (this is the grand-prize demo moment)
  bdata scraper heal <collector_id> "<describe what's wrong and what correct output should look like>"
  # Human-in-the-loop by default — proposes a diff, stops at an approval gate.
  # `approve` commits it, or add --auto-approve to skip the gate.
  ```
- **Backend:** Python + `brightdata-sdk` (Python SDK) to trigger collectors programmatically for recurring runs rather than shelling out to the CLI each time. SQLite or a free-tier Postgres (Supabase/Neon) for storage.
- **Classification:** Type 2 (EOL) is a plain date comparison — no model needed. Type 1 (breaking change) needs an LLM pass over raw changelog text via the Anthropic API — ask for structured JSON output (`breaking: bool`, `reason: string`).
- **Frontend:** Next.js + React, deployed to Vercel for a live demo URL.

## Data schemas

**Agent inventory (posted by each host):**
```json
{
  "hostname": "web-01",
  "distro": "ubuntu-22.04",
  "kernel": "5.15.0",
  "packages": [
    {"name": "openssl", "version": "1.1.1f", "manager": "apt"},
    {"name": "python3", "version": "3.7.0", "manager": "apt"}
  ]
}
```

**Collector A raw extraction (changelog):**
```json
{"package": "django", "version": "4.0", "release_date": "2021-12-07",
 "changelog_text": "USE_L10N setting is removed. Localized formatting is enabled..."}
```

**Collector B raw extraction (EOL):**
```json
{"package": "python", "version": "3.7", "eol_date": "2023-06-27"}
```

**Classification output:**
```json
{"package": "python", "flag": "eol", "detail": "3.7 EOL'd 2023-06-27"}
{"package": "django", "version": "4.0", "flag": "breaking", "reason": "removed USE_L10N setting"}
```

**Final radar entry (what the dashboard shows, joined against fleet inventory):**
```json
{
  "hostname": "web-01",
  "package": "python", "installed_version": "3.7", "current_stable": "3.13",
  "flags": [{"type": "eol", "detail": "past support since 2023-06-27"}]
}
```

## Suggested starter watchlist (for demo breadth across ecosystems)

Python, Django, Node.js, OpenSSL, and one or two popular npm packages — enough spread across PyPI/apt/npm to make the self-healing story (different page structures per source) land clearly.

## Build order

1. Scaffold the repo: agent/, backend/, frontend/, README skeleton.
2. Build Collector A (changelog/release pages) via `bdata scraper create`, test against 2–3 packages.
3. Build Collector B (EOL/support pages), test against the same packages.
4. Wire `brightdata-sdk` into the backend to trigger both collectors and persist raw JSON.
5. Build classification (date logic for EOL, Claude API call for breaking-change detection).
6. Build the correlation logic that joins fleet inventory against classified radar data.
7. Build the agent script (distro detection, package inventory, POST to backend).
8. Build the Next.js dashboard, deploy to Vercel.
9. Deliberately stage a self-heal moment for the demo — break a collector's extraction on purpose (or find a page that's genuinely drifted), run `bdata scraper heal`, show the diff, approve it, rerun.
10. Write the README, record the demo video, write the Scraper Studio usage explanation for submission.

## How to work with me on this

- Confirm the plan for each stage before writing code, and work through the build order incrementally rather than generating everything at once.
- Flag anywhere you're making an architectural assumption so we can catch it early.
- Keep the code clean and commented enough that any team member can explain it — that's both a rule requirement and a judged criterion (Best Clean Code / Spider-Sense track).
- Ask before installing anything outside the stack listed above.

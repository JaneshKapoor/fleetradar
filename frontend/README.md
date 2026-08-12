# Fleet Radar dashboard

Next.js + React, deployed to Vercel. Scaffolded in Stage 8.

Reads `public/radar.json` — a snapshot exported from the backend's SQLite
database by the pipeline's export step. See the "Why SQLite + a JSON snapshot"
section of [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) for why the
dashboard reads static data rather than querying a hosted database.

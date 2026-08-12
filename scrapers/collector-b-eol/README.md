# Collector B — EOL / support pages

**Feeds:** Type 2 (end-of-support) detection.

**Extracts:** `package`, `version`, `eol_date`
(see `EolEntry` in `backend/fleetradar/models.py`).

A `null` `eol_date` means the source lists the version as still supported — it is
not a scrape failure, and the classifier treats the two differently.

Populated in Stage 3.

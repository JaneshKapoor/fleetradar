# Collector A — changelog / release pages

**Feeds:** Type 1 (breaking change) detection.

**Extracts:** `package`, `version`, `release_date`, `changelog_text`
(see `ChangelogEntry` in `backend/fleetradar/models.py`).

`changelog_text` is captured raw and unparsed on purpose — the Stage 5 classifier
reads the prose, so trimming it here would discard the exact signal we need.

Populated in Stage 2.

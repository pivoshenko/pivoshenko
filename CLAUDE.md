# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

GitHub profile repo for `pivoshenko`. Two responsibilities:

1. **`README.md`** — public profile page. Sections between `<!-- STATS:START -->`/`<!-- NOTABLE:START -->`/`<!-- UPDATED:START -->` markers are auto-generated; everything else is hand-written. Never edit inside the markers by hand.
2. **`scripts/`** — Python automation that runs on a schedule against the GitHub API:
   - `update_readme_stats.py` — refreshes the marker-delimited sections in `README.md` (totals + top notable external contributions filtered by `NOTABLE_MIN_STARS` and `NOTABLE_LIMIT`).
   - `set_repository_policies.py` — applies cross-repo policy defaults (e.g. disabling wikis) across all of the owner's non-fork repos via `PATCH /repos/{owner}/{repo}`.

Both scripts require `GH_TOKEN` and `GITHUB_REPOSITORY_OWNER` (see `.env.example`). They are normally invoked from `.github/workflows/` and locally via `just`.

## Commands

```
just install   # uv sync --all-groups --all-extras
just format    # pyupgrade (py313+) over scripts/, then ruff check --fix ., then ruff format .
just lint      # ruff check . && ruff format --check . && ty check
just audit     # pip-audit
just check     # lint (CI gate)
just update    # uvx uv-upsync && uv sync
just stats     # run update_readme_stats.py locally
just policies  # run set_repository_policies.py locally
```

Python is pinned to **3.13** (`requires-python = ">=3.13"`, ruff `target-version = "py313"`, `ty` env matches). Package manager is **uv**; do not introduce pip/poetry.

Note: `.github/workflows/ci.yaml` calls `just test`, but there is no `test` recipe and no test suite — adding one is the obvious unblock if a test fails in CI.

## Code conventions

- Ruff `select = ["ALL"]` with only `D`, `G004`, `INP001` ignored — expect to satisfy almost every rule. `unsafe-fixes = true`.
- Isort config forces single-line imports, `from-first = false`, `length-sort-straight = true`, **2 lines after imports**, **1 line between import types**, and **`from __future__ import annotations` is a required import in every module**.
- Format-on-fix is on (`ruff.fix = true`); prefer `just format` over manual edits when restructuring imports.
- Line length 100, double-quoted strings, docstring code blocks are formatted.

## Parent workspace

This repo sits inside `~/Development/sources/`, which has its own `CLAUDE.md` describing the broader monorepo-ish layout and group conventions. This repo is in the **`personal`** group there. The root-level `just <verb>-personal` recipes fan verbs out across the personal group, so keep the recipe vocabulary (`install`/`format`/`lint`/`check`/`update`) aligned with sibling repos.

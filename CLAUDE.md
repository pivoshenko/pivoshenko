# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the GitHub profile repository (`pivoshenko/pivoshenko`) for Volodymyr Pivoshenko. It contains automation scripts that maintain the GitHub profile README and enforce repository policies across all owned repos.

## Commands

All commands use `uv` as the package manager and `just` as the task runner.

```bash
just format    # Run pyupgrade + ruff format on scripts/
just lint      # Run ty type checker + ruff linter
just update    # Upgrade uv.lock and sync pyproject.toml
```

Running scripts directly (requires `GH_TOKEN` and `GITHUB_REPOSITORY_OWNER` env vars from `.env`):

```bash
uv run python scripts/update_readme_stats.py
uv run python scripts/set_repository_policies.py
```

## Architecture

- **`scripts/update_readme_stats.py`** — Fetches GitHub stats (stars, commits, PRs, issues) and notable contributions via the GitHub GraphQL API, then patches `README.md` between HTML comment markers (`<!-- STATS:START -->`, `<!-- NOTABLE:START -->`, `<!-- UPDATED:START -->`).
- **`scripts/set_repository_policies.py`** — Enforces org-wide repo settings via the GitHub REST API: disables wiki/projects/discussions, sets rebase-only merge, and prefixes fork names with `fork-`.
- **`.github/workflows/`** — `update-readme-stats.yaml` runs weekly (Monday 10:00 UTC) on cron + manual dispatch; `set-repository-policies.yaml` is manual dispatch only.

## Code Style

- Python 3.13+, all files must include `from __future__ import annotations`
- Ruff with `select = ["ALL"]`, ignoring `D` (docstrings), `G004`, `INP001`
- Line length: 100
- Imports: single-line, sorted by length, stdlib-first
- Formatting: double quotes, ruff format
- Type checking: `ty`

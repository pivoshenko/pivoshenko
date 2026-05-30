# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the GitHub profile repository (`pivoshenko/pivoshenko`) for Volodymyr Pivoshenko. It contains automation scripts that maintain the GitHub profile README and enforce repository policies across all owned repos.

## Commands

All commands use `uv` as the package manager and `just` as the task runner.

```bash
just install   # uv sync
just format    # Run pyupgrade + ruff format on scripts/
just lint      # Run ruff linter + ty type checker
just audit     # uv audit — scan deps for known vulns
just check     # Full gate (same as lint — no build step)
just update    # Upgrade uv.lock and sync pyproject.toml
```

Script-runner recipes (require `GH_TOKEN` and `GITHUB_REPOSITORY_OWNER` env vars from `.env`):

```bash
just stats     # uv run python scripts/update_readme_stats.py
just policies  # uv run python scripts/set_repository_policies.py
```

Workflows invoke ONLY `just <recipe>` (per the CI contract) — never `uv run …` directly. Add a recipe before adding a workflow step.

## Architecture

- **`scripts/update_readme_stats.py`** — Fetches GitHub stats (stars, commits, PRs, issues) and notable contributions via the GitHub GraphQL API, then patches `README.md` between HTML comment markers (`<!-- STATS:START -->`, `<!-- NOTABLE:START -->`, `<!-- UPDATED:START -->`).
- **`scripts/set_repository_policies.py`** — Enforces org-wide repo settings via the GitHub REST API: disables wiki/projects/discussions, sets rebase-only merge, and prefixes fork names with `fork-`.
- **`.github/workflows/`** — `update-readme-stats.yaml` runs weekly (Monday 10:00 UTC) on cron + manual dispatch; `set-repository-policies.yaml` is manual dispatch only.

## Code Style

- Python 3.13+, all files must include `from __future__ import annotations`
- Ruff with `select = ["ALL"]`, ignoring `D` (docstrings), `G004`, `INP001`
- Line length: 100
- Imports: single-line, sorted by length (`force-single-line`, `length-sort-straight`; `from-first = false` → default isort grouping)
- Formatting: double quotes, ruff format
- Type checking: `ty`

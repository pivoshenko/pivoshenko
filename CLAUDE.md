# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal GitHub profile repository for Volodymyr Pivoshenko. Contains two Python automation scripts:
- `scripts/update_readme_stats.py` — aggregates GitHub stats (stars, commits, PRs, issues, notable contributions) and updates `README.md` via regex on HTML comment markers (`<!-- STATS:START -->`, `<!-- NOTABLE_CONTRIBUTIONS:START -->`)
- `scripts/set_repository_policies.py` — enforces consistent repository settings across all owned GitHub repos (disables wiki/projects/discussions, rebase-only merges, prefixes forks with "fork-")

## Commands

```bash
just format   # pyupgrade --py313-plus + ruff format
just lint     # ty check + ruff check + cz check (commit messages)
just update   # uv lock --upgrade + uvx uv-upsync
```

Run scripts directly:
```bash
uv run python scripts/update_readme_stats.py
uv run python scripts/set_repository_policies.py
```

Scripts require environment variables: `GH_TOKEN`, `GITHUB_REPOSITORY_OWNER`.

## Code Standards

- Python 3.13+ — use modern syntax (match/case, `X | Y` unions, etc.)
- Ruff is configured with nearly all rules enabled; only `D`, `G004`, `INP001` are ignored
- Line length: 100 characters
- Type checking via `ty` (not mypy)
- Commits must follow commitizen conventions — run `just lint` to validate

## Architecture Notes

Both scripts follow the same pattern: paginated GitHub API calls → data aggregation → side effect (README update or API mutations). `httpx` is used for all HTTP (sync client), `loguru` for logging.

The README update script uses GraphQL for reads; the policy script uses REST. Neither script has tests — they are run directly in CI.

CI runs on GitHub Actions: stats update is scheduled (Monday 10 AM UTC), policy enforcement is manual-dispatch only.

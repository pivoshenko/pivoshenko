# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The GitHub profile repository for `pivoshenko` (`github.com/pivoshenko/pivoshenko`). It has exactly two jobs:

1. **`README.md`** — the rendered profile page. The regions between `<!-- STATS:START -->`/`<!-- STATS:END -->`, `<!-- NOTABLE:START -->`/`<!-- NOTABLE:END -->`, and `<!-- UPDATED:START -->`/`<!-- UPDATED:END -->` are machine-generated; everything outside them is hand-written prose. Never hand-edit inside the markers — the next scheduled run overwrites them.
2. **`scripts/`** — two standalone Python scripts driven by GitHub Actions. There is no package, no `src/`, no importable module; each script is a flat file with a `if __name__ == "__main__"` block.

## Commands

```sh
just              # list recipes
just install      # uv sync --all-groups --all-extras
just format       # pyupgrade --py313-plus over all .py (excl .venv) -> ruff check --fix -> ruff format
just lint         # ruff check . && ty check
just audit        # pip-audit
just test         # no-op: prints "skipping (.no-tests sentinel)" while .no-tests exists
just check        # lint + test
just update       # uv lock --upgrade && uvx uv-upsync
just stats        # run scripts/update_readme_stats.py locally (needs GH_TOKEN)
just policies     # run scripts/set_repository_policies.py locally (needs GH_TOKEN) -- MUTATES ALL REPOS
```

Package manager is **uv**; Python is pinned to **3.13** (`requires-python`, ruff `target-version = "py313"`, `[tool.ty.environment]`). Do not introduce pip/poetry/pytest configuration.

Gotcha: only `just install` uses the synced `.venv`. The `format`/`lint`/`audit`/`update` recipes shell out through `uvx`, which resolves the *latest* ruff/ty/pyupgrade rather than the versions pinned in `[dependency-groups]`. A clean `just lint` locally can still differ from CI if the pins are stale; bump the pins in `pyproject.toml` when new rules start firing.

There are no tests and no test framework. `.no-tests` is a deliberate sentinel file — deleting it makes `just test` fail hard by design.

## CI and automation (`.github/workflows/`)

- `ci.yaml` — a single flat `ci` job on `ubuntu-24.04-arm`, triggered on push to `main`, all PRs, and dispatch. Steps run sequentially: `just install` → `just lint` → `just audit` → test. The test step re-implements the `.no-tests` check inline in bash rather than calling `just test`, so that guard exists in two places; keep them in sync.
- `update-readme-stats.yaml` — cron `0 10 * * 1` (Mondays 10:00 UTC) plus dispatch. Runs `just stats`, then commits `README.md` back to `main` as `github-actions[bot]` (`|| exit 0` when nothing changed). Needs `contents: write`.
- `set-repository-policies.yaml` — `workflow_dispatch` **only**, never scheduled. This is intentional: the script mutates every repo on the account.

Both scripts read `GH_TOKEN` and `GITHUB_REPOSITORY_OWNER` (see `.env.example`); workflows pass the ambient `secrets.GITHUB_TOKEN`.

## `scripts/update_readme_stats.py`

Talks to the GitHub **GraphQL** API (`POST /graphql` via a shared `httpx.Client`; `graphql()` raises on a non-empty `errors` array). It gathers four numbers and one list:

- stars — paginates all non-fork repos owned by the user, sums `stargazerCount`
- commits — reads the account creation year, then loops year-by-year over `contributionsCollection`, adding `totalCommitContributions + restrictedContributionsCount` (private contributions included)
- PRs / issues — lifetime `totalCount`
- notable contributions — walks merged PRs newest-first for at most `NOTABLE_MAX_PAGES` (5) pages of 100, keeps repos not owned by the user with at least `NOTABLE_MIN_STARS` (100) stars, dedupes by `nameWithOwner`, sorts by stars, takes `NOTABLE_LIMIT` (10)

Rendering is plain string joins; `update_readme()` swaps each marker block with a `re.sub(..., flags=re.DOTALL)`. `fmt()` abbreviates at 1k/1M with one decimal. Changing the README's visible layout means changing `render_stats`/`render_notable`/`render_updated`, not `README.md` itself.

## `scripts/set_repository_policies.py`

Uses the GitHub **REST** API. Destructive and account-wide — read it before running it. For every non-fork, non-archived repo it `PATCH`es: `has_wiki=false`, `has_projects=false`, `has_discussions=false`, and merge method to rebase-only (`allow_merge_commit=false`, `allow_squash_merge=false`, `allow_rebase_merge=true`). Then, for every fork, it **renames** the repo to `fork-<name>` unless already prefixed.

Two things to know before editing it:

- the `httpx.Client` (`api`) is constructed at *module import* time and reads `os.environ["GH_TOKEN"]` there, so importing the module without the env var raises immediately
- `list_repositories()`/`list_forked_repositories()` call `GET /user/repos` with no pagination, so they only ever see the first page (~30 repos)

## Code conventions

- Ruff `select = ["ALL"]` with only `CPY001`, `D`, `G004`, `INP001` ignored — assume nearly every rule applies. `fix = true` and `unsafe-fixes = true`, so `ruff check` rewrites code on every run; prefer `just format` over hand-restructuring.
- Isort is configured unusually: `force-single-line = true`, `from-first = false`, `length-sort-straight = true`, 2 blank lines after imports, 1 blank line between import types, and `from __future__ import annotations` is a `required-imports` entry in every module.
- Line length 100 (ruff), double-quoted strings, `docstring-code-format = true`. `.editorconfig` sets 4-space indent for Python (2 elsewhere) and a looser 120 guide — ruff's 100 wins.
- Module docstrings open with `Module that contains ...`; packages would use `Package that contains ...`. House style, not lint-enforced (`D` is ignored).
- `G004` is ignored specifically so loguru f-string logging (`logger.info(f"...")`) is allowed — that is the established logging style here.
- Commits follow Angular conventional commits (`docs:`, `chore:`, `ci:`, `build(deps):`). Issue/PR labels are declared in `.github/labels.yaml` under the `type: `, `priority: `, `status: ` prefixes.

# CLAUDE.md

## Read This First

- **`scripts/set_repository_policies.py` is a live, irreversible, account-wide mutation.** It touches other repositories, not this one, and renaming a fork changes its URL. Its workflow is `workflow_dispatch`-only for that reason. Do not run it to "test a change" - if you modify it, reason about the diff rather than executing it
- **The marker regions in `README.md` are generated. Do not hand-edit them** - the next scheduled run silently overwrites your changes. To change what appears there, edit the `render_*` functions in `scripts/update_readme_stats.py`. The markers themselves must stay exactly as written; `update_readme` matches them with `re.sub`, and a missing marker means that section is silently skipped, not an error. The README's prose outside the markers is hand-written and safe to edit
- **`.env` holds a real token.** It is gitignored - never read it into output, echo it, or commit it
- **`just lint` mutates files despite its name.** `[tool.ruff]` sets `fix = true` and `unsafe-fixes = true`, which apply to every `ruff check` invocation, including the one inside `lint`. Use `uvx ruff check --no-fix .` when you want a pure verification pass
- **`AGENTS.md` is a symlink to `CLAUDE.md`.** Edit this file and both change; never replace the symlink with a real file

## What This Repo Is

`pivoshenko/pivoshenko` - GitHub's special profile repository. Two things live here:

1. `README.md`, which GitHub renders on <https://github.com/pivoshenko>
2. A pair of Python automation scripts that talk to the GitHub API: one regenerates parts of that README, the other applies account-wide repository settings

There is no application, library, or package to import. `pyproject.toml` declares a project named `pivoshenko` only so `uv` has something to sync against; nothing is published.

## Commands

`just --list` for the full set, `CONTRIBUTING.md` for what each recipe and workflow does. What neither tells you:

- linters and formatters run via `uvx`, not from the project venv. The `formatters` and `linters` dependency groups exist so the versions are pinned and lockable, but the recipes invoke ephemeral `uvx` tools. `just install` is only needed for the scripts' own runtime deps
- `.no-tests` is a sentinel, not a config file. Deleting it makes `just test` and CI fail until a real test command is wired into the `test` recipe. Add tests and the recipe together, or leave it alone
- both scripts read `GITHUB_REPOSITORY_OWNER` and `GH_TOKEN` (see `.env.example`); in Actions `GH_TOKEN` is the auto-provided `secrets.GITHUB_TOKEN`

## Scripts

Both are standalone entry points guarded by `if __name__ == "__main__"`, with no package `__init__.py` - which is why `INP001` is in the Ruff ignore list.

`update_readme_stats.py` fetches aggregate account numbers over the GitHub GraphQL API and rewrites three marker-delimited regions of `README.md` in place (`STATS`, `NOTABLE`, `UPDATED`). Shape of the fetch: stars paginate over owned non-fork repos, commits are summed year-by-year from account creation to now (so the count includes `restrictedContributionsCount`), and notable contributions are merged PRs into repos the user does not own, capped at `NOTABLE_MAX_PAGES` pages of 100 and filtered by `NOTABLE_MIN_STARS`.

`set_repository_policies.py` lists repos with `GET /user/repos`, then disables wiki, projects, and discussions on every non-fork, non-archived one and forces rebase-only merges, and renames every fork to `fork-<name>` (skipping any already prefixed). Its reach is narrower and less predictable than that sounds:

- both `list_repositories()` and `list_forked_repositories()` call `/user/repos` with no `per_page` and no pagination, so they only ever see GitHub's default first page. It is not every repo on the account
- `/user/repos` returns every repo the token's user can access, org and collaborator repos included, while every PATCH is hardcoded to `/repos/{GITHUB_REPOSITORY_OWNER}/{name}`. A non-owned repo in that page yields a 404 that `raise_for_status()` turns into a hard abort mid-run

## Conventions

Ruff runs with `select = ["ALL"]` and a short, deliberate ignore list; the isort settings make imports sort by line length rather than alphabetically, and `from __future__ import annotations` is a `required-imports` entry. All of it lives in `pyproject.toml` and `just format` applies it - do not hand-arrange imports.

Modules carry a one-line `"""Module that contains the script that ..."""` header; follow that phrasing for new scripts.

Commit and branch conventions: see `CONTRIBUTING.md`.

default:
    @just --list

install:
    uv sync --all-groups --all-extras

format:
    uv run ruff check --fix .
    uv run ruff format .

lint:
    uv run ruff check .
    uv run ty check .

test:
    @[ -f .no-tests ] && echo "skipping (.no-tests sentinel)" || { echo "no test command, add tests or restore .no-tests" >&2; exit 1; }

check: lint test

update:
    uv lock --upgrade
    uvx uv-upsync

set-repository-policies:
    uv run python scripts/set_repository_policies.py

update-readme-stats:
    uv run python scripts/update_readme_stats.py

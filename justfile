default:
    @just --list

install:
    uv sync --all-groups --all-extras

format:
    find . -type f -name '*.py' -not -path '*/.venv/*' | xargs uvx pyupgrade --py313-plus
    uvx ruff check --fix .
    uvx ruff format .

lint:
    uvx ruff check .
    uvx ruff format --check .
    uvx ty check

audit:
    uvx pip-audit

test:
    @[ -f .no-tests ] && echo "skipping (.no-tests sentinel)" || { echo "no test command — add tests or restore .no-tests" >&2; exit 1; }

check: lint test

update:
    uv lock --upgrade
    uvx uv-upsync

stats:
    uv run python scripts/update_readme_stats.py

policies:
    uv run python scripts/set_repository_policies.py

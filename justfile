default:
    @just --list

install:
    uv sync --all-groups --all-extras

format:
    find scripts -type f -name '*.py' | xargs uvx pyupgrade --py313-plus
    uvx ruff check --fix .
    uvx ruff format .

lint:
    uvx ruff check .
    uvx ruff format --check .
    uvx ty check

audit:
    uvx pip-audit

check: lint

update:
    uvx uv-upsync
    uv sync

stats:
    uv run python scripts/update_readme_stats.py

policies:
    uv run python scripts/set_repository_policies.py

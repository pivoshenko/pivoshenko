default:
    @just --list

install:
    uv sync

format:
    find scripts -type f -name '*.py' | xargs uv run pyupgrade --py313-plus
    uv run ruff format .

lint:
    uv run ruff check .
    uv run ty check .

audit:
    uv audit

check: lint

update:
    uv lock --upgrade
    uvx uv-upsync

stats:
    uv run python scripts/update_readme_stats.py

policies:
    uv run python scripts/set_repository_policies.py

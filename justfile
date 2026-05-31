default:
    @just --list

install:
    uv sync --all-groups --all-extras

format:
    find src -type f -name '*.py' | xargs uv run pyupgrade --py313-plus
    uv run ruff format .

lint:
    uv run ty check .
    uv run ruff check .

audit:
    uv audit

check: lint audit

update:
    uv lock --upgrade
    uvx uv-upsync

stats:
    uv run python scripts/update_readme_stats.py

policies:
    uv run python scripts/set_repository_policies.py

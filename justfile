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

check: lint

update:
    uv lock --upgrade
    uvx uv-upsync

stats:
    uv run python scripts/update_readme_stats.py

policies:
    uv run python scripts/set_repository_policies.py

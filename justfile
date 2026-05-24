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

check: lint

update:
    uv lock --upgrade
    uvx uv-upsync

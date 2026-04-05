format:
  find scripts -type f -name '*.py' | xargs uv run pyupgrade --py313-plus
  uv run ruff format .

lint:
  uv run ty check .
  uv run ruff check .

update:
  uv lock --upgrade
  uvx uv-upsync

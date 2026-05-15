# CLI / batch jobs (Python)

**Map:** `argparse` / scripts → **Clikt** + coroutines in Kotlin (`clikt`, `kotlinx.coroutines`).

## Layout

- `python/` — argparse subcommands (`uv` + `pytest`)
- `kotlin/` — Clikt subcommands (`./gradlew test` / `./gradlew run`)

## Python

```bash
cd python && uv sync --extra dev && uv run pytest -q && uv run mypy src
uv run python -m cli_batch_demo.cli upper --input README.md
```

## Kotlin

```bash
cd kotlin && ./gradlew test && ./gradlew run --args='upper --input ../python/README.md'
```

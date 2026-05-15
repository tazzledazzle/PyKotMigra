"""Allow ``python -m pykotmig`` (avoids ``uv run pykotmig`` vs package name clash)."""

from pykotmig.cli.main import main

if __name__ == "__main__":
    main()

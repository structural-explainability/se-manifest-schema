"""Module entry point for se-manifest-schema.

Enables `uv run python -m se_manifest_schema`.
Delegates immediately to the CLI entry point.
All logic lives in cli.py, validate.py, sync.py, and load.py.
"""

from se_manifest_schema.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

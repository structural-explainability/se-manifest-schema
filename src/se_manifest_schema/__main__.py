"""Allow running as a module: python -m se_manifest_schema."""

from se_manifest_schema.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

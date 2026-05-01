"""cli.py - Command-line interface for se-manifest-schema.

Parses arguments and dispatches to orchestrate.py or sync.py.
Owns nothing except argument parsing and error handling.
All logic lives in orchestrate.py and sync.py.

Entry points:
  uv run python -m se_manifest_schema validate
  uv run python -m se_manifest_schema validate --strict
  uv run python -m se_manifest_schema validate --require-tag
  uv run python -m se_manifest_schema sync

Call chain:
  __main__.py -> cli.main()
              -> orchestrate.run_validate()  (sync_all called internally)
              -> sync.sync_all()             (sync only, no validation)
"""

import argparse

from se_manifest_schema.orchestrate import run_validate
from se_manifest_schema.sync import sync_all


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="se-manifest-schema",
        description="Sync and validate the SE manifest schema.",
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate",
        help="Sync and validate manifest-schema.toml and SE_MANIFEST.toml.",
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    validate_parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Require CITATION.cff version to match current git tag.",
    )

    subparsers.add_parser(
        "sync",
        help="Sync pyproject.toml fallback-version from CITATION.cff version.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface.

    Returns:
        0 on success, 1 on error, 2 if no command given.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            return run_validate(
                strict=args.strict,
                require_tag=args.require_tag,
            )
        if args.command == "sync":
            sync_all()
            return 0

    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        return 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

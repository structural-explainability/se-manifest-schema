"""src/se_manifest_schema/cli.py.

Command-line interface.
Pure dispatcher; owns argument parsing only.
All logic lives in commands/.

Entry points:
  uv run se-manifest validate
  uv run se-manifest validate --strict --require-tag
  uv run se-manifest validate --path path/to/SE_MANIFEST.toml
  uv run se-manifest validate-schema
  uv run se-manifest validate-schema --strict
  uv run se-manifest sync-version

  uv run python -m se_manifest_schema validate
  uv run python -m se_manifest_schema validate-schema
  uv run python -m se_manifest_schema sync-version
"""

import argparse
from pathlib import Path

from se_manifest_schema.commands import sync_version, validate, validate_schema


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="se-manifest",
        description="Validate and sync SE_MANIFEST.toml files for se Interfaces repos.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # === validate ===
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate SE_MANIFEST.toml against the schema. Safe for all repos.",
    )
    validate_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to SE_MANIFEST.toml (default: ./SE_MANIFEST.toml).",
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

    # === validate-schema ===
    vs_parser = subparsers.add_parser(
        "validate-schema",
        help="Validate manifest-schema.toml internal consistency. This repo only.",
    )
    vs_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    vs_parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Require CITATION.cff version to match current git tag.",
    )

    # === sync-version ===
    subparsers.add_parser(
        "sync-version",
        help="Sync pyproject.toml fallback-version from CITATION.cff. This repo only.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface.

    Returns:
        0 on success, 1 on error, 2 if no command given.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate.run(
            path=args.path,
            strict=args.strict,
            require_tag=args.require_tag,
        )

    if args.command == "validate-schema":
        return validate_schema.run(
            strict=args.strict,
            require_tag=args.require_tag,
        )

    if args.command == "sync-version":
        return sync_version.run()

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

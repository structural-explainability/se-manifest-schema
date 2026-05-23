"""Command-line interface for se-manifest-schema.

This module parses arguments and dispatches commands.
Command behavior lives in se_manifest_schema.commands.

Commands:
uv run se-manifest validate-schema

uv run se-manifest validate-manifest
uv run se-manifest validate-manifest --strict

uv run se-manifest check-version
uv run se-manifest check-version --require-tag
"""

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from se_manifest_schema.commands import (
    check_version,
    validate_manifest,
    validate_schema,
)

__all__ = ["build_parser", "main"]

CommandFunc = Callable[[argparse.Namespace], int]

EXIT_NO_COMMAND = 2


def _run_check_version(args: argparse.Namespace) -> int:
    """Check that the version is consistent across CITATION.cff and pyproject.toml."""
    return check_version.run(require_tag=args.require_tag)


def _run_validate_manifest(args: argparse.Namespace) -> int:
    """Validate a repository manifest against the schema."""
    return validate_manifest.run(
        path=args.path,
        strict=args.strict,
        require_tag=args.require_tag,
    )


def _run_validate_schema(args: argparse.Namespace) -> int:
    """Validate manifest-schema.toml internal consistency."""
    return validate_schema.run(strict=args.strict)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="se-manifest",
        description="Validate SE repository manifests.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    # === CHECK VERSION COMMAND ===

    version_parser = subparsers.add_parser(
        "check-version",
        help=(
            "Check that CITATION.cff and pyproject.toml fallback-version agree. "
            "Reports a mismatch; does not modify any file."
        ),
    )
    version_parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Also require the version to match the current git tag.",
    )
    version_parser.set_defaults(func=_run_check_version)

    # === VALIDATE MANIFEST COMMAND ===

    validate_parser = subparsers.add_parser(
        "validate-manifest",
        help="Validate MANIFEST.toml or SE_MANIFEST.toml against the SE schema.",
    )
    validate_parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help=(
            "Path to SE_MANIFEST.toml or MANIFEST.toml. "
            "Defaults to the first supported manifest found."
        ),
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    validate_parser.add_argument(
        "--require-tag",
        action="store_true",
        help="Require CITATION.cff version to match the current git tag.",
    )
    validate_parser.set_defaults(func=_run_validate_manifest)

    # === VALIDATE SCHEMA COMMAND ===

    schema_parser = subparsers.add_parser(
        "validate-schema",
        help="Validate manifest-schema.toml internal consistency.",
    )
    schema_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    schema_parser.set_defaults(func=_run_validate_schema)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface.

    Args:
        argv: Optional list of command-line arguments. If None, uses sys.argv.

    Returns:
        Exit code from the executed command, or EXIT_NO_COMMAND if no command was given.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    func: CommandFunc | None = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return EXIT_NO_COMMAND

    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())

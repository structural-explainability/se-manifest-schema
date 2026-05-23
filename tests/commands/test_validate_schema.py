"""Tests for commands/validate_schema.py."""

from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.commands.validate_schema import run

REPO_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "manifest-schema.toml"


def test_validate_schema_invalid_schema_returns_1(tmp_path: Path) -> None:
    """A schema file with an invalid field type returns 1."""
    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(
        """
[section.repo]
allowed_fields = ["name"]

[field.repo]
name = {type = "not-a-valid-type", required = true}

[class]

[validation]
""",
        encoding="utf-8",
    )

    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=schema_path,
    ):
        result: int = run()

    assert result == 1


def test_validate_schema_missing_schema_file_returns_1() -> None:
    """Missing manifest-schema.toml returns 1."""
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=None,
    ):
        result: int = run()

    assert result == 1


def test_validate_schema_passes() -> None:
    """run() against this repo's own manifest-schema.toml returns 0."""
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=SCHEMA_PATH,
    ):
        result: int = run()

    assert result == 0


def test_validate_schema_strict_passes_when_no_warnings() -> None:
    """strict is accepted and returns 0 when there are no schema errors."""
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=SCHEMA_PATH,
    ):
        result: int = run(strict=True)

    assert result == 0

"""tests/commands/test_validate_schema.py.

Tests for commands/validate_schema.py - schema internal consistency command.
"""

from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.commands.validate_schema import run

REPO_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "manifest-schema.toml"


def test_validate_schema_passes() -> None:
    """run() against this repo's own manifest-schema.toml must return 0."""
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=SCHEMA_PATH,
    ):
        result = run()

    assert result == 0


def test_validate_schema_strict_passes_when_no_warnings() -> None:
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=SCHEMA_PATH,
    ):
        result = run(strict=True)

    assert result == 0


def test_validate_schema_missing_schema_file_returns_1() -> None:
    with patch(
        "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
        return_value=None,
    ):
        result = run()

    assert result == 1


def test_validate_schema_require_tag_fails_when_not_on_tag() -> None:
    with (
        patch(
            "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
            return_value=SCHEMA_PATH,
        ),
        patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ),
    ):
        result = run(require_tag=True)

    assert result == 1


def test_validate_schema_strict_and_require_tag_together() -> None:
    """--strict and --require-tag can be combined."""
    with (
        patch(
            "se_manifest_schema.commands.validate_schema.repo_root_schema_path",
            return_value=SCHEMA_PATH,
        ),
        patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ),
    ):
        result = run(strict=True, require_tag=True)

    assert result == 1


def test_validate_schema_invalid_schema_returns_1(tmp_path: Path) -> None:
    """A schema file with an invalid field type should fail."""
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
        result = run()

    assert result == 1

"""Tests for commands/check_version.py."""

from unittest.mock import patch

from se_manifest_schema.commands.check_version import run


def test_check_version_passes_require_tag() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.check_version_run",
        return_value=0,
    ) as check_version_run:
        result: int = run(require_tag=True)

    assert result == 0
    check_version_run.assert_called_once_with(require_tag=True)


def test_check_version_returns_0_when_versions_agree() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.check_version_run",
        return_value=0,
    ) as check_version_run:
        result: int = run()

    assert result == 0
    check_version_run.assert_called_once_with(require_tag=False)


def test_check_version_returns_1_on_file_not_found() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.check_version_run",
        side_effect=FileNotFoundError("CITATION.cff not found"),
    ):
        result: int = run()

    assert result == 1


def test_check_version_returns_1_on_runtime_error() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.check_version_run",
        side_effect=RuntimeError("not on a tagged commit"),
    ):
        result: int = run(require_tag=True)

    assert result == 1


def test_check_version_returns_1_on_value_error() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.check_version_run",
        side_effect=ValueError("invalid version"),
    ):
        result: int = run()

    assert result == 1

"""tests/test_cli.py.

Tests for cli.py - argument parsing and dispatch.
"""

import os
from pathlib import Path
from typing import Final
from unittest.mock import patch

import pytest

from se_manifest_schema.cli import build_parser, main
from se_manifest_schema.commands.validate_manifest import run

MANIFEST_FILE_NAME: Final[str] = "SE_MANIFEST.toml"


def test_build_parser_returns_parser() -> None:
    parser = build_parser()
    assert parser is not None


def test_main_check_version_returns_0() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.run",
        return_value=0,
    ) as check_version_run:
        result: int = main(["check-version"])

    assert result == 0
    check_version_run.assert_called_once_with(require_tag=False)


def test_main_check_version_require_tag_returns_0() -> None:
    with patch(
        "se_manifest_schema.commands.check_version.run",
        return_value=0,
    ) as check_version_run:
        result: int = main(["check-version", "--require-tag"])

    assert result == 0
    check_version_run.assert_called_once_with(require_tag=True)


def test_main_handles_file_not_found_gracefully(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = main(["validate-manifest"])
        assert result == 1
    finally:
        os.chdir(old)


def test_main_no_command_returns_2() -> None:
    result = main([])
    assert result == 2


def test_main_validate_own_manifest_returns_0() -> None:
    repo_root = Path(__file__).parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        result = main(["validate-manifest"])
        assert result == 0
    finally:
        os.chdir(old)


def test_main_validate_explicit_path_returns_0() -> None:
    repo_root = Path(__file__).parent.parent
    result = main(["validate-manifest", "--path", str(repo_root / MANIFEST_FILE_NAME)])
    assert result == 0


def test_main_validate_missing_path_returns_1(tmp_path: Path) -> None:
    result = main(["validate-manifest", "--path", str(tmp_path / MANIFEST_FILE_NAME)])
    assert result == 1


def test_main_validate_require_tag_fails_when_not_tagged() -> None:
    repo_root = Path(__file__).parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ):
            result = main(["validate-manifest", "--require-tag"])
            assert result == 1
    finally:
        os.chdir(old)


def test_main_validate_schema_returns_0() -> None:
    with patch(
        "se_manifest_schema.commands.validate_schema.run",
        return_value=0,
    ) as validate_schema_run:
        result: int = main(["validate-schema"])

    assert result == 0
    validate_schema_run.assert_called_once_with(strict=False)


def test_main_validate_schema_strict_returns_0() -> None:
    with patch(
        "se_manifest_schema.commands.validate_schema.run",
        return_value=0,
    ) as validate_schema_run:
        result: int = main(["validate-schema", "--strict"])

    assert result == 0
    validate_schema_run.assert_called_once_with(strict=True)


def test_main_validate_strict_returns_0() -> None:
    repo_root = Path(__file__).parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        result = main(["validate-manifest", "--strict"])
        assert result == 0
    finally:
        os.chdir(old)


def test_validate_own_manifest_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    result = run()
    assert result == 0

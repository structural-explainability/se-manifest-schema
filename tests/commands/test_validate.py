"""tests/commands/test_validate.py.

Tests for commands/validate.py - validation command.
"""

import os
from pathlib import Path
from typing import Final
from unittest.mock import patch

from se_manifest_schema.commands.validate import run

MANIFEST_FILE_NAME: Final[str] = "SE_MANIFEST.toml"


def test_validate_own_manifest_passes() -> None:
    """run() against this repo's own manifest file must return 0."""
    repo_root = Path(__file__).parent.parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        result = run()
        assert result == 0
    finally:
        os.chdir(old)


def test_validate_explicit_path_passes() -> None:
    repo_root = Path(__file__).parent.parent.parent
    result = run(path=repo_root / MANIFEST_FILE_NAME)
    assert result == 0


def test_validate_missing_manifest_returns_1(tmp_path: Path) -> None:
    result = run(path=tmp_path / MANIFEST_FILE_NAME)
    assert result == 1


def test_validate_missing_schema_returns_1(tmp_path: Path) -> None:
    (tmp_path / MANIFEST_FILE_NAME).write_text(
        'schema = "se-interfaces-manifest-schema"\n', encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run()
        assert result == 1
    finally:
        os.chdir(old)


def test_validate_strict_passes_when_no_warnings() -> None:
    repo_root = Path(__file__).parent.parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        result = run(strict=True)
        assert result == 0
    finally:
        os.chdir(old)


def test_validate_require_tag_fails_when_not_on_tag() -> None:
    repo_root = Path(__file__).parent.parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ):
            result = run(require_tag=True)
            assert result == 1
    finally:
        os.chdir(old)


def test_validate_strict_and_require_tag_together() -> None:
    """--strict and --require-tag can be combined."""
    repo_root = Path(__file__).parent.parent.parent
    old = Path.cwd()
    os.chdir(repo_root)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ):
            result = run(strict=True, require_tag=True)
            assert result == 1
    finally:
        os.chdir(old)

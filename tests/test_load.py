"""Tests for load.py - file loading and parsing."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from se_manifest_schema.load import (
    get_git_tag,
    get_repo_version,
    load_manifest,
    load_schema,
    load_toml,
)


def test_get_git_tag_not_found(tmp_path: Path) -> None:
    with (
        patch("shutil.which", return_value=None),
        pytest.raises(RuntimeError, match="git executable"),
    ):
        get_git_tag()


def test_load_toml_valid(tmp_path: Path) -> None:
    f = tmp_path / "test.toml"
    f.write_text('[meta]\nversion = "1.0.0"\n', encoding="utf-8")
    data = load_toml(f)
    assert data["meta"]["version"] == "1.0.0"


def test_load_schema_found(tmp_path: Path) -> None:
    (tmp_path / "manifest-schema.toml").write_text(
        '[meta]\nversion = "1.0.0"\n', encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        data = load_schema()
        assert "meta" in data
    finally:
        os.chdir(old)


def test_load_schema_missing(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(FileNotFoundError, match="manifest-schema.toml"):
            load_schema()
    finally:
        os.chdir(old)


def test_load_manifest_missing(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(FileNotFoundError, match="SE_MANIFEST.toml"):
            load_manifest()
    finally:
        os.chdir(old)


def test_get_repo_version_valid() -> None:
    manifest = {"repo": {"version": "0.2.0", "name": "x"}}
    assert get_repo_version(manifest) == "0.2.0"


def test_get_repo_version_missing_repo() -> None:
    with pytest.raises(ValueError, match="repo"):
        get_repo_version({})


def test_get_repo_version_missing_version() -> None:
    with pytest.raises(ValueError, match="version"):
        get_repo_version({"repo": {"name": "x"}})

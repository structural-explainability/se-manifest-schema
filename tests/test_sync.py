"""Tests for sync.py - version sync from CITATION.cff to pyproject.toml."""

from pathlib import Path

import pytest

from se_manifest_schema.sync import get_version_from_citation, sync_pyproject


def test_get_version_from_citation_valid(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: '1.2.0'\nversion: 0.2.0\n", encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        assert get_version_from_citation() == "0.2.0"
    finally:
        os.chdir(old)


def test_get_version_from_citation_missing(tmp_path: Path) -> None:
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(FileNotFoundError, match="CITATION.cff"):
            get_version_from_citation()
    finally:
        os.chdir(old)


def test_sync_pyproject_updates_version(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        sync_pyproject("0.2.0")
        assert 'fallback-version = "0.2.0"' in pyproject.read_text(encoding="utf-8")
    finally:
        os.chdir(old)


def test_sync_pyproject_missing_field(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test'\n", encoding="utf-8")
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(ValueError, match="fallback-version"):
            sync_pyproject("0.2.0")
    finally:
        os.chdir(old)

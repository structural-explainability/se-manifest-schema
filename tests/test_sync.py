"""Tests for sync.py - version propagation from CITATION.cff."""

import os
from pathlib import Path

import pytest

from se_manifest_schema.sync import get_version_from_citation, sync_pyproject


def test_get_version_from_citation(tmp_path: Path) -> None:
    """Reads version correctly from a valid CITATION.cff."""
    (tmp_path / "CITATION.cff").write_text(
        "version: 1.2.3\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        assert get_version_from_citation() == "1.2.3"
    finally:
        os.chdir(old)


def test_get_version_missing_file(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(FileNotFoundError, match="CITATION.cff"):
            get_version_from_citation()
    finally:
        os.chdir(old)


def test_get_version_missing_field(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text("title: Something\n", encoding="utf-8")
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(ValueError, match="version"):
            get_version_from_citation()
    finally:
        os.chdir(old)


def test_sync_pyproject_updates_fallback(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        sync_pyproject("2.0.0")
        assert 'fallback-version = "2.0.0"' in pyproject.read_text(encoding="utf-8")
    finally:
        os.chdir(old)


def test_sync_pyproject_missing_file(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(FileNotFoundError, match="pyproject.toml"):
            sync_pyproject("1.0.0")
    finally:
        os.chdir(old)


def test_sync_pyproject_missing_field(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'x'\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(ValueError, match="fallback-version"):
            sync_pyproject("1.0.0")
    finally:
        os.chdir(old)


def test_sync_pyproject_multiple_fields(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        'fallback-version = "0.1.0"\nfallback-version = "0.1.0"\n',
        encoding="utf-8",
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(ValueError, match="fallback-version"):
            sync_pyproject("1.0.0")
    finally:
        os.chdir(old)

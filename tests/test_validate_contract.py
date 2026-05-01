"""Tests for validate_contract.py - tag alignment."""

import os
from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.validate_contract import validate_tag


def test_tag_matches_version(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "version: 1.0.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag", return_value="v1.0.0"
        ):
            assert validate_tag({}) == []
    finally:
        os.chdir(old)


def test_tag_mismatch_detected(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "version: 1.0.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag", return_value="v2.0.0"
        ):
            errors = validate_tag({})
    finally:
        os.chdir(old)
    assert any("v2.0.0" in e for e in errors)


def test_not_on_tag_detected(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "version: 1.0.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on tagged commit"),
        ):
            errors = validate_tag({})
    finally:
        os.chdir(old)
    assert any("tagged" in e for e in errors)


def test_citation_missing(tmp_path: Path) -> None:
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        errors = validate_tag({})
    finally:
        os.chdir(old)
    assert any("CITATION.cff" in e for e in errors)

"""tests/test_validate_contract.py.

Tests for validate_contract.py - version and tag alignment.
"""

from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.validate_contract import validate_tag


def test_validate_tag_passes_when_versions_match(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: '1.2.0'\nversion: 0.2.0\n", encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            return_value="v0.2.0",
        ):
            errors = validate_tag({})
            assert errors == []
    finally:
        os.chdir(old)


def test_validate_tag_fails_when_versions_mismatch(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: '1.2.0'\nversion: 0.2.0\n", encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            return_value="v0.1.0",
        ):
            errors = validate_tag({})
            assert any("0.2.0" in e and "0.1.0" in e for e in errors)
    finally:
        os.chdir(old)


def test_validate_tag_fails_when_not_on_tagged_commit(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: '1.2.0'\nversion: 0.2.0\n", encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            side_effect=RuntimeError("not on a tagged commit"),
        ):
            errors = validate_tag({})
            assert any("tagged commit" in e for e in errors)
    finally:
        os.chdir(old)


def test_validate_tag_fails_when_citation_missing(tmp_path: Path) -> None:
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        errors = validate_tag({})
        assert any("CITATION.cff" in e for e in errors)
    finally:
        os.chdir(old)


def test_validate_tag_fails_when_citation_missing_version(tmp_path: Path) -> None:
    (tmp_path / "CITATION.cff").write_text(
        "cff-version: '1.2.0'\ntitle: no version here\n", encoding="utf-8"
    )
    import os

    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        errors = validate_tag({})
        assert any("version" in e for e in errors)
    finally:
        os.chdir(old)

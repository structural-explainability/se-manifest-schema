"""Tests for check_version.py."""

from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.check_version import (
    EXIT_MISMATCH,
    EXIT_OK,
    get_fallback_version,
    get_version_from_citation,
    run,
)

MATCHING_VERSION = "1.2.3"
DIFFERENT_VERSION = "1.2.4"
MATCHING_TAG = f"v{MATCHING_VERSION}"
DIFFERENT_TAG = f"v{DIFFERENT_VERSION}"


def test_get_fallback_version_reads_pyproject(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(
        """
[tool.hatch.version]
fallback-version = "1.2.3"
""",
        encoding="utf-8",
    )

    assert get_fallback_version(path) == MATCHING_VERSION


def test_get_fallback_version_missing_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"

    try:
        get_fallback_version(path)
    except FileNotFoundError as exc:
        assert "pyproject.toml not found" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_get_fallback_version_missing_field_raises(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text("[tool.hatch.version]\n", encoding="utf-8")

    try:
        get_fallback_version(path)
    except ValueError as exc:
        assert "fallback-version" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_get_version_from_citation_missing_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "CITATION.cff"

    try:
        get_version_from_citation(path)
    except FileNotFoundError as exc:
        assert "CITATION.cff not found" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_get_version_from_citation_missing_version_raises(tmp_path: Path) -> None:
    path = tmp_path / "CITATION.cff"
    path.write_text("cff-version: 1.2.0\n", encoding="utf-8")

    try:
        get_version_from_citation(path)
    except ValueError as exc:
        assert "version" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_get_version_from_citation_reads_unquoted_version(tmp_path: Path) -> None:
    path = tmp_path / "CITATION.cff"
    path.write_text(
        f"cff-version: 1.2.0\nversion: {MATCHING_VERSION}\n", encoding="utf-8"
    )

    assert get_version_from_citation(path) == MATCHING_VERSION


def test_get_version_from_citation_reads_quoted_version(tmp_path: Path) -> None:
    path = tmp_path / "CITATION.cff"
    path.write_text(f'version: "{MATCHING_VERSION}"\n', encoding="utf-8")

    assert get_version_from_citation(path) == MATCHING_VERSION


def test_run_returns_mismatch_when_fallback_differs() -> None:
    with (
        patch(
            "se_manifest_schema.check_version.get_version_from_citation",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_fallback_version",
            return_value=DIFFERENT_VERSION,
        ),
    ):
        result = run()

    assert result == EXIT_MISMATCH


def test_run_returns_mismatch_when_tag_differs() -> None:
    with (
        patch(
            "se_manifest_schema.check_version.get_version_from_citation",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_fallback_version",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_git_tag", return_value=DIFFERENT_TAG
        ),
    ):
        result = run(require_tag=True)

    assert result == EXIT_MISMATCH


def test_run_returns_ok_when_tag_matches_with_v_prefix() -> None:
    with (
        patch(
            "se_manifest_schema.check_version.get_version_from_citation",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_fallback_version",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_git_tag", return_value=MATCHING_TAG
        ),
    ):
        result = run(require_tag=True)

    assert result == EXIT_OK


def test_run_returns_ok_when_versions_match() -> None:
    with (
        patch(
            "se_manifest_schema.check_version.get_version_from_citation",
            return_value=MATCHING_VERSION,
        ),
        patch(
            "se_manifest_schema.check_version.get_fallback_version",
            return_value=MATCHING_VERSION,
        ),
    ):
        result = run()

    assert result == EXIT_OK

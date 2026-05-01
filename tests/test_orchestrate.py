"""Tests for orchestrate.py - validation orchestrator."""

import os
from pathlib import Path
from unittest.mock import patch

from se_manifest_schema.orchestrate import run_validate


def _write_valid_files(tmp_path: Path) -> None:
    """Write minimal valid CITATION.cff, pyproject.toml, manifest-schema.toml, SE_MANIFEST.toml."""
    (tmp_path / "CITATION.cff").write_text(
        "version: 0.1.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "manifest-schema.toml").write_text(
        """
[manifest.identity]
schema_required = true
schema_allowed = ["se-manifest-2"]
schema_url_required = true

[section.repo]
required = true
allowed_fields = ["name", "class"]

[section.scope]
required = true
allowed_fields = ["includes", "excludes"]

[field.repo.name]
type = "string"
required = true

[field.repo.class]
type = "string"
required = true

[field.scope.includes]
type = "list[string]"
required = true

[field.scope.excludes]
type = "list[string]"
required = true

[class.test_class]
required_sections = ["repo", "scope"]
optional_sections = []
forbidden_sections = []
required_compatibility_fields = []

[validation]
require_known_sections_only = true
require_known_fields_only = true
""",
        encoding="utf-8",
    )
    (tmp_path / "SE_MANIFEST.toml").write_text(
        """
schema = "se-manifest-2"
schema_url = "https://example.com"

[repo]
name = "se-test"
class = "test_class"

[scope]
includes = ["something"]
excludes = []
""",
        encoding="utf-8",
    )


def test_run_validate_passes(tmp_path: Path) -> None:
    """run_validate returns 0 when all files are valid."""
    _write_valid_files(tmp_path)
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate()
        assert result == 0
    finally:
        os.chdir(old)


def test_run_validate_missing_schema(tmp_path: Path) -> None:
    """run_validate returns 1 when manifest-schema.toml is missing."""
    (tmp_path / "CITATION.cff").write_text(
        "version: 0.1.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "SE_MANIFEST.toml").write_text(
        'schema = "se-manifest-2"\nschema_url = "https://example.com"\n',
        encoding="utf-8",
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate()
        assert result == 1
    finally:
        os.chdir(old)


def test_run_validate_missing_manifest(tmp_path: Path) -> None:
    """run_validate returns 1 when SE_MANIFEST.toml is missing."""
    (tmp_path / "CITATION.cff").write_text(
        "version: 0.1.0\ndate-released: 2026-01-01\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "manifest-schema.toml").write_text(
        "[meta]\nversion = '0.1.0'\n", encoding="utf-8"
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate()
        assert result == 1
    finally:
        os.chdir(old)


def test_run_validate_schema_errors(tmp_path: Path) -> None:
    """run_validate returns 1 when schema has internal errors."""
    _write_valid_files(tmp_path)
    schema = tmp_path / "manifest-schema.toml"
    text = schema.read_text(encoding="utf-8")
    # introduce a broken class referencing unknown section
    text += '\n[class.broken]\nrequired_sections = ["nonexistent"]\n'
    schema.write_text(text, encoding="utf-8")
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate()
        assert result == 1
    finally:
        os.chdir(old)


def test_run_validate_manifest_errors(tmp_path: Path) -> None:
    """run_validate returns 1 when manifest does not conform to schema."""
    _write_valid_files(tmp_path)
    # overwrite manifest with missing required section
    (tmp_path / "SE_MANIFEST.toml").write_text(
        'schema = "se-manifest-2"\nschema_url = "https://example.com"\n'
        '[repo]\nname = "se-test"\nclass = "test_class"\n',
        encoding="utf-8",
    )
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate()
        assert result == 1
    finally:
        os.chdir(old)


def test_run_validate_require_tag_match(tmp_path: Path) -> None:
    """run_validate returns 0 when tag matches version."""
    _write_valid_files(tmp_path)
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            return_value="v0.1.0",
        ):
            result = run_validate(require_tag=True)
        assert result == 0
    finally:
        os.chdir(old)


def test_run_validate_require_tag_mismatch(tmp_path: Path) -> None:
    """run_validate returns 1 when tag does not match version."""
    _write_valid_files(tmp_path)
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "se_manifest_schema.validate_contract.get_git_tag",
            return_value="v9.9.9",
        ):
            result = run_validate(require_tag=True)
        assert result == 1
    finally:
        os.chdir(old)


def test_run_validate_strict_no_warnings(tmp_path: Path) -> None:
    """run_validate returns 0 in strict mode when there are no warnings."""
    _write_valid_files(tmp_path)
    old = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = run_validate(strict=True)
        assert result == 0
    finally:
        os.chdir(old)

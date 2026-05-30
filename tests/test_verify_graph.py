"""Tests for commands/verify_graph.py - graph verification command."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from se_manifest_schema.commands.verify_graph import (
    _find_schema_repo,
    _looks_like_schema_repo,
    _resolve_path,
    _resolve_report_path,
    _resolve_root,
    _resolve_schema_path,
    run,
)


# ── _looks_like_schema_repo ────────────────────────────────────────────────────

def test_looks_like_schema_repo_true(tmp_path: Path) -> None:
    repo = tmp_path / "se-manifest-schema"
    repo.mkdir()
    (repo / "manifest-schema.toml").write_text("[schema]\n", encoding="utf-8")
    (repo / "SE_MANIFEST.toml").write_text("[repo]\n", encoding="utf-8")
    assert _looks_like_schema_repo(repo) is True


def test_looks_like_schema_repo_wrong_name(tmp_path: Path) -> None:
    repo = tmp_path / "other-repo"
    repo.mkdir()
    (repo / "manifest-schema.toml").write_text("[schema]\n", encoding="utf-8")
    (repo / "SE_MANIFEST.toml").write_text("[repo]\n", encoding="utf-8")
    assert _looks_like_schema_repo(repo) is False


def test_looks_like_schema_repo_missing_schema_file(tmp_path: Path) -> None:
    repo = tmp_path / "se-manifest-schema"
    repo.mkdir()
    (repo / "SE_MANIFEST.toml").write_text("[repo]\n", encoding="utf-8")
    assert _looks_like_schema_repo(repo) is False


def test_looks_like_schema_repo_missing_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "se-manifest-schema"
    repo.mkdir()
    (repo / "manifest-schema.toml").write_text("[schema]\n", encoding="utf-8")
    assert _looks_like_schema_repo(repo) is False


# ── _find_schema_repo ──────────────────────────────────────────────────────────

def test_find_schema_repo_finds_ancestor(tmp_path: Path) -> None:
    schema_repo = tmp_path / "se-manifest-schema"
    schema_repo.mkdir()
    (schema_repo / "manifest-schema.toml").write_text("[schema]\n", encoding="utf-8")
    (schema_repo / "SE_MANIFEST.toml").write_text("[repo]\n", encoding="utf-8")

    nested = schema_repo / "nested" / "subdir"
    nested.mkdir(parents=True)

    result = _find_schema_repo(nested)
    assert result == schema_repo.resolve()


def test_find_schema_repo_finds_child(tmp_path: Path) -> None:
    schema_repo = tmp_path / "se-manifest-schema"
    schema_repo.mkdir()
    (schema_repo / "manifest-schema.toml").write_text("[schema]\n", encoding="utf-8")
    (schema_repo / "SE_MANIFEST.toml").write_text("[repo]\n", encoding="utf-8")

    result = _find_schema_repo(tmp_path)
    assert result == schema_repo.resolve()


def test_find_schema_repo_falls_back_to_working_dir(tmp_path: Path) -> None:
    result = _find_schema_repo(tmp_path)
    assert result == tmp_path.resolve()


# ── _resolve_path ──────────────────────────────────────────────────────────────

def test_resolve_path_absolute(tmp_path: Path) -> None:
    absolute = tmp_path / "file.toml"
    absolute.touch()
    result = _resolve_path(absolute, working_dir=tmp_path, schema_repo=tmp_path)
    assert result == absolute.resolve()


def test_resolve_path_relative_to_working_dir(tmp_path: Path) -> None:
    file = tmp_path / "file.toml"
    file.touch()
    result = _resolve_path(Path("file.toml"), working_dir=tmp_path, schema_repo=tmp_path)
    assert result == file.resolve()


def test_resolve_path_relative_to_schema_repo(tmp_path: Path) -> None:
    schema_repo = tmp_path / "schema-repo"
    schema_repo.mkdir()
    file = schema_repo / "schema-file.toml"
    file.touch()

    other = tmp_path / "other"
    other.mkdir()

    result = _resolve_path(
        Path("schema-file.toml"),
        working_dir=other,
        schema_repo=schema_repo,
    )
    assert result == file.resolve()


def test_resolve_path_fallback_to_working_dir_candidate(tmp_path: Path) -> None:
    # Neither cwd nor schema_repo have the file; fallback to cwd candidate
    result = _resolve_path(
        Path("missing.toml"),
        working_dir=tmp_path,
        schema_repo=tmp_path,
    )
    assert result == (tmp_path / "missing.toml").resolve()


# ── _resolve_root ──────────────────────────────────────────────────────────────

def test_resolve_root_explicit(tmp_path: Path) -> None:
    explicit = tmp_path / "custom-root"
    explicit.mkdir()
    schema_repo = tmp_path / "schema-repo"

    result = _resolve_root(root=explicit, working_dir=tmp_path, schema_repo=schema_repo)
    assert result == explicit.resolve()


def test_resolve_root_defaults_to_parent_when_schema_repo(tmp_path: Path) -> None:
    schema_repo = tmp_path / "se-manifest-schema"
    schema_repo.mkdir()
    (schema_repo / "manifest-schema.toml").write_text("", encoding="utf-8")
    (schema_repo / "SE_MANIFEST.toml").write_text("", encoding="utf-8")

    result = _resolve_root(root=None, working_dir=schema_repo, schema_repo=schema_repo)
    assert result == tmp_path.resolve()


def test_resolve_root_defaults_to_working_dir(tmp_path: Path) -> None:
    working_dir = tmp_path / "some-other-dir"
    working_dir.mkdir()
    schema_repo = tmp_path / "unrelated"
    schema_repo.mkdir()

    result = _resolve_root(root=None, working_dir=working_dir, schema_repo=schema_repo)
    assert result == working_dir.resolve()


# ── _resolve_schema_path ────────────────────────────────────────────────────────

def test_resolve_schema_path_explicit(tmp_path: Path) -> None:
    explicit = tmp_path / "my-schema.toml"
    explicit.touch()
    schema_repo = tmp_path

    result = _resolve_schema_path(
        schema_path=explicit, working_dir=tmp_path, schema_repo=schema_repo
    )
    assert result == explicit.resolve()


def test_resolve_schema_path_defaults_to_schema_repo(tmp_path: Path) -> None:
    schema_repo = tmp_path / "se-manifest-schema"
    schema_repo.mkdir()

    result = _resolve_schema_path(
        schema_path=None, working_dir=tmp_path, schema_repo=schema_repo
    )
    assert result == (schema_repo / "manifest-schema.toml").resolve()


# ── _resolve_report_path ────────────────────────────────────────────────────────

def test_resolve_report_path_explicit(tmp_path: Path) -> None:
    explicit = tmp_path / "report.md"
    explicit.touch()
    schema_repo = tmp_path

    result = _resolve_report_path(
        report_path=explicit, working_dir=tmp_path, schema_repo=schema_repo
    )
    assert result == explicit.resolve()


def test_resolve_report_path_defaults_to_schema_repo(tmp_path: Path) -> None:
    schema_repo = tmp_path / "se-manifest-schema"
    schema_repo.mkdir()

    result = _resolve_report_path(
        report_path=None, working_dir=tmp_path, schema_repo=schema_repo
    )
    assert "org-graph-report.md" in str(result)


# ── run ────────────────────────────────────────────────────────────────────────

def test_run_passes_with_no_manifests(tmp_path: Path) -> None:
    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text("[class]\n", encoding="utf-8")
    report_path = tmp_path / "report.md"

    result = run(root=tmp_path, schema_path=schema_path, report_path=report_path)
    assert result == 0
    assert report_path.exists()


def test_run_fails_when_diagnostics(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo-a"
    repo_dir.mkdir()
    manifest = repo_dir / "SE_MANIFEST.toml"
    manifest.write_text(
        """
[repo]
name = "repo-a"
class = "core"
version = "0.1.0"
status = "active"

[layer]
space = "theory"
role = "kernel"

[depends]
required = ["ghost-repo"]
""",
        encoding="utf-8",
    )

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(
        "[class.core]\nrequired_sections = [\"repo\"]\n", encoding="utf-8"
    )
    report_path = tmp_path / "report.md"

    result = run(root=tmp_path, schema_path=schema_path, report_path=report_path)
    assert result == 1


def test_run_writes_report_file(tmp_path: Path) -> None:
    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text("[class]\n", encoding="utf-8")
    report_path = tmp_path / "sub" / "report.md"

    run(root=tmp_path, schema_path=schema_path, report_path=report_path)
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Manifest Graph Report" in content

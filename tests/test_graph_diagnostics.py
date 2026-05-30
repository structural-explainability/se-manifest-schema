"""Tests for graph/diagnostics.py - GraphDiagnostic rendering."""

from pathlib import Path

from se_manifest_schema.graph.diagnostics import GraphDiagnostic


def test_render_code_only() -> None:
    d = GraphDiagnostic(code="SE.ORG.TEST", message="something went wrong")
    result = d.render()
    assert result.startswith("SE.ORG.TEST")
    assert "something went wrong" in result


def test_render_with_repo() -> None:
    d = GraphDiagnostic(code="SE.ORG.TEST", message="bad repo", repo="my-repo")
    result = d.render()
    assert "my-repo" in result


def test_render_with_path_absolute() -> None:
    d = GraphDiagnostic(
        code="SE.ORG.TEST",
        message="artifact missing",
        path="/some/abs/path/file.toml",
    )
    result = d.render()
    assert "/some/abs/path/file.toml" in result


def test_render_with_path_relative_to_root(tmp_path: Path) -> None:
    artifact = tmp_path / "sub" / "file.toml"
    d = GraphDiagnostic(
        code="SE.ORG.TEST",
        message="artifact missing",
        path=str(artifact),
    )
    result = d.render(root=tmp_path)
    assert "sub/file.toml" in result
    assert str(tmp_path) not in result


def test_render_with_path_outside_root_falls_back_to_full(tmp_path: Path) -> None:
    other_root = tmp_path / "other"
    artifact = tmp_path / "somewhere" / "file.toml"
    d = GraphDiagnostic(
        code="SE.ORG.TEST",
        message="artifact missing",
        path=str(artifact),
    )
    result = d.render(root=other_root)
    assert artifact.as_posix() in result


def test_render_with_root_as_string(tmp_path: Path) -> None:
    artifact = tmp_path / "sub" / "file.toml"
    d = GraphDiagnostic(
        code="SE.ORG.TEST",
        message="artifact missing",
        path=str(artifact),
    )
    result = d.render(root=str(tmp_path))
    assert "sub/file.toml" in result


def test_render_all_fields() -> None:
    d = GraphDiagnostic(
        code="SE.ORG.CYCLE",
        message="dependency cycle detected",
        repo="repo-a",
        path="/some/path",
    )
    result = d.render()
    lines = result.splitlines()
    assert lines[0] == "SE.ORG.CYCLE"
    assert any("repo-a" in line for line in lines)
    assert any("/some/path" in line for line in lines)
    assert any("dependency cycle detected" in line for line in lines)


def test_render_without_repo_or_path() -> None:
    d = GraphDiagnostic(code="SE.ORG.GENERIC", message="something failed")
    result = d.render()
    lines = result.splitlines()
    assert len(lines) == 2
    assert lines[0] == "SE.ORG.GENERIC"
    assert "something failed" in lines[1]

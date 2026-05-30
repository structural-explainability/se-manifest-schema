"""Tests for graph/report.py - Markdown report rendering."""

from pathlib import Path
from typing import Any

from se_manifest_schema.graph.diagnostics import GraphDiagnostic
from se_manifest_schema.graph.model import DependencyEdge, GraphRepository, ManifestGraph
from se_manifest_schema.graph.report import render_markdown_report


def _make_repo(name: str, tmp_path: Path) -> GraphRepository:
    return GraphRepository(
        name=name,
        repo_class="core",
        layer_space="theory",
        layer_role="kernel",
        status="active",
        root=tmp_path / name,
        manifest_path=tmp_path / name / "SE_MANIFEST.toml",
        manifest={},
        provided_artifacts=(),
    )


def _make_graph(
    repos: dict[str, GraphRepository],
    edges: list[DependencyEdge],
    schema: dict[str, Any] | None = None,
) -> ManifestGraph:
    return ManifestGraph(
        repositories=repos,
        edges=tuple(edges),
        missing_manifest_roots=(),
        manifest_schema=schema or {},
    )


def test_render_empty_graph(tmp_path: Path) -> None:
    graph = _make_graph({}, [])
    report = render_markdown_report(graph=graph, diagnostics=[])
    assert "# Manifest Graph Report" in report
    assert "Repositories: 0" in report
    assert "Dependencies: 0" in report
    assert "Diagnostics: 0" in report
    assert "No diagnostics." in report
    assert "No dependencies." in report


def test_render_with_repositories(tmp_path: Path) -> None:
    repos = {
        "repo-a": _make_repo("repo-a", tmp_path),
        "repo-b": _make_repo("repo-b", tmp_path),
    }
    graph = _make_graph(repos, [])
    report = render_markdown_report(graph=graph, diagnostics=[])
    assert "Repositories: 2" in report
    assert "repo-a" in report
    assert "repo-b" in report


def test_render_with_dependencies(tmp_path: Path) -> None:
    repos = {
        "repo-a": _make_repo("repo-a", tmp_path),
        "repo-b": _make_repo("repo-b", tmp_path),
    }
    edges = [
        DependencyEdge(source="repo-a", target="repo-b", required=True, kind="semantic"),
    ]
    graph = _make_graph(repos, edges)
    report = render_markdown_report(graph=graph, diagnostics=[])
    assert "Dependencies: 1" in report
    assert "repo-a" in report
    assert "repo-b" in report
    assert "required" in report
    assert "semantic" in report


def test_render_with_optional_dependency(tmp_path: Path) -> None:
    repos = {
        "repo-a": _make_repo("repo-a", tmp_path),
        "repo-b": _make_repo("repo-b", tmp_path),
    }
    edges = [
        DependencyEdge(source="repo-a", target="repo-b", required=False, kind="artifact"),
    ]
    graph = _make_graph(repos, edges)
    report = render_markdown_report(graph=graph, diagnostics=[])
    assert "optional" in report


def test_render_with_diagnostics(tmp_path: Path) -> None:
    repos = {"repo-a": _make_repo("repo-a", tmp_path)}
    graph = _make_graph(repos, [])
    diagnostics = [
        GraphDiagnostic(
            code="SE.ORG.CYCLE",
            message="dependency cycle detected",
            repo="repo-a",
        )
    ]
    report = render_markdown_report(graph=graph, diagnostics=diagnostics)
    assert "Diagnostics: 1" in report
    assert "SE.ORG.CYCLE" in report
    assert "dependency cycle detected" in report


def test_render_returns_string_ending_with_newline(tmp_path: Path) -> None:
    graph = _make_graph({}, [])
    report = render_markdown_report(graph=graph, diagnostics=[])
    assert isinstance(report, str)
    assert report.endswith("\n")

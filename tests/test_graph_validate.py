"""Tests for graph/validate.py - SI invariant validation."""

from pathlib import Path
from typing import Any

import pytest

from se_manifest_schema.graph.diagnostics import GraphDiagnostic
from se_manifest_schema.graph.model import DependencyEdge, GraphRepository, ManifestGraph
from se_manifest_schema.graph.validate import validate_si_invariants


def _make_repo(
    name: str,
    root: Path,
    repo_class: str = "core",
    provided_artifacts: tuple[str, ...] = (),
    manifest: dict[str, Any] | None = None,
) -> GraphRepository:
    manifest_path = root / name / "SE_MANIFEST.toml"
    return GraphRepository(
        name=name,
        repo_class=repo_class,
        layer_space="theory",
        layer_role="kernel",
        status="active",
        root=root / name,
        manifest_path=manifest_path,
        manifest=manifest if manifest is not None else {"repo": {"name": name, "class": repo_class}},
        provided_artifacts=provided_artifacts,
    )


def _make_graph(
    repos: dict[str, GraphRepository],
    edges: list[DependencyEdge],
    schema: dict[str, Any] | None = None,
    tmp_path: Path | None = None,
) -> ManifestGraph:
    if schema is None:
        schema = {
            "class": {
                "core": {"required_sections": ["repo"]},
            }
        }
    return ManifestGraph(
        repositories=repos,
        edges=tuple(edges),
        missing_manifest_roots=(),
        manifest_schema=schema,
    )


# ── SI01: required semantic graph is acyclic ────────────────────────────────────

def test_si01_no_cycles(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
    }
    edges = [DependencyEdge(source="a", target="b", required=True, kind="semantic")]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    cycle_diags = [d for d in diags if d.code == "SE.ORG.DEPENDENCY_CYCLE"]
    assert cycle_diags == []


def test_si01_direct_cycle_detected(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
    }
    edges = [
        DependencyEdge(source="a", target="b", required=True, kind="semantic"),
        DependencyEdge(source="b", target="a", required=True, kind="semantic"),
    ]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    cycle_diags = [d for d in diags if d.code == "SE.ORG.DEPENDENCY_CYCLE"]
    assert len(cycle_diags) >= 1


def test_si01_three_node_cycle_detected(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
        "c": _make_repo("c", tmp_path),
    }
    edges = [
        DependencyEdge(source="a", target="b", required=True, kind="semantic"),
        DependencyEdge(source="b", target="c", required=True, kind="semantic"),
        DependencyEdge(source="c", target="a", required=True, kind="semantic"),
    ]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    cycle_diags = [d for d in diags if d.code == "SE.ORG.DEPENDENCY_CYCLE"]
    assert len(cycle_diags) >= 1


def test_si01_optional_edge_does_not_trigger_cycle_check(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
    }
    edges = [
        DependencyEdge(source="a", target="b", required=False, kind="semantic"),
        DependencyEdge(source="b", target="a", required=False, kind="semantic"),
    ]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    cycle_diags = [d for d in diags if d.code == "SE.ORG.DEPENDENCY_CYCLE"]
    assert cycle_diags == []


def test_si01_non_semantic_required_edge_not_checked_for_cycle(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
    }
    edges = [
        DependencyEdge(source="a", target="b", required=True, kind="artifact"),
        DependencyEdge(source="b", target="a", required=True, kind="artifact"),
    ]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    cycle_diags = [d for d in diags if d.code == "SE.ORG.DEPENDENCY_CYCLE"]
    assert cycle_diags == []


# ── SI02: all declared dependencies resolve ─────────────────────────────────────

def test_si02_all_resolve(tmp_path: Path) -> None:
    repos = {
        "a": _make_repo("a", tmp_path),
        "b": _make_repo("b", tmp_path),
    }
    edges = [DependencyEdge(source="a", target="b", required=True, kind="semantic")]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    unresolved = [d for d in diags if d.code == "SE.ORG.UNRESOLVED_DEPENDENCY"]
    assert unresolved == []


def test_si02_unresolved_dependency_detected(tmp_path: Path) -> None:
    repos = {"a": _make_repo("a", tmp_path)}
    edges = [DependencyEdge(source="a", target="missing-repo", required=True, kind="semantic")]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    unresolved = [d for d in diags if d.code == "SE.ORG.UNRESOLVED_DEPENDENCY"]
    assert len(unresolved) == 1
    assert "missing-repo" in unresolved[0].message


def test_si02_optional_unresolved_also_reported(tmp_path: Path) -> None:
    repos = {"a": _make_repo("a", tmp_path)}
    edges = [DependencyEdge(source="a", target="ghost", required=False, kind="semantic")]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    unresolved = [d for d in diags if d.code == "SE.ORG.UNRESOLVED_DEPENDENCY"]
    assert len(unresolved) == 1


# ── SI03: provided artifacts exist ─────────────────────────────────────────────

def test_si03_artifact_exists(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-a"
    repo_root.mkdir()
    artifact = repo_root / "output.json"
    artifact.write_text("{}", encoding="utf-8")

    repo = _make_repo("repo-a", tmp_path, provided_artifacts=("output.json",))
    repos = {"repo-a": repo}
    graph = _make_graph(repos, [])
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_PROVIDED_ARTIFACT"]
    assert missing == []


def test_si03_missing_artifact_reported(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-a"
    repo_root.mkdir()

    repo = _make_repo("repo-a", tmp_path, provided_artifacts=("nonexistent.json",))
    repos = {"repo-a": repo}
    graph = _make_graph(repos, [])
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_PROVIDED_ARTIFACT"]
    assert len(missing) == 1
    assert "nonexistent.json" in missing[0].message


def test_si03_multiple_missing_artifacts(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-a"
    repo_root.mkdir()

    repo = _make_repo(
        "repo-a",
        tmp_path,
        provided_artifacts=("missing1.json", "missing2.json"),
    )
    repos = {"repo-a": repo}
    graph = _make_graph(repos, [])
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_PROVIDED_ARTIFACT"]
    assert len(missing) == 2


def test_si03_no_artifacts_no_diagnostics(tmp_path: Path) -> None:
    repo = _make_repo("repo-a", tmp_path, provided_artifacts=())
    graph = _make_graph({"repo-a": repo}, [])
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_PROVIDED_ARTIFACT"]
    assert missing == []


# ── SI04: class registry requirements satisfied ─────────────────────────────────

def test_si04_unknown_class_reported(tmp_path: Path) -> None:
    repo = _make_repo("repo-a", tmp_path, repo_class="unknown_class")
    repos = {"repo-a": repo}
    schema: dict[str, Any] = {"class": {"core": {"required_sections": ["repo"]}}}
    graph = _make_graph(repos, [], schema=schema)
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_REQUIRED_SECTION"]
    assert any("unknown manifest class" in d.message for d in missing)


def test_si04_required_section_present(tmp_path: Path) -> None:
    repo = _make_repo(
        "repo-a",
        tmp_path,
        repo_class="core",
        manifest={"repo": {"name": "repo-a", "class": "core"}},
    )
    repos = {"repo-a": repo}
    schema: dict[str, Any] = {"class": {"core": {"required_sections": ["repo"]}}}
    graph = _make_graph(repos, [], schema=schema)
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_REQUIRED_SECTION"]
    assert missing == []


def test_si04_missing_required_section_reported(tmp_path: Path) -> None:
    repo = _make_repo(
        "repo-a",
        tmp_path,
        repo_class="core",
        manifest={"repo": {"name": "repo-a", "class": "core"}},
    )
    repos = {"repo-a": repo}
    schema: dict[str, Any] = {"class": {"core": {"required_sections": ["repo", "layer"]}}}
    graph = _make_graph(repos, [], schema=schema)
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_REQUIRED_SECTION"]
    assert any("layer" in d.message for d in missing)


def test_si04_invalid_required_sections_type_reported(tmp_path: Path) -> None:
    repo = _make_repo("repo-a", tmp_path, repo_class="core")
    repos = {"repo-a": repo}
    schema: dict[str, Any] = {"class": {"core": {"required_sections": "not-a-list"}}}
    graph = _make_graph(repos, [], schema=schema)
    diags = validate_si_invariants(graph)
    missing = [d for d in diags if d.code == "SE.ORG.MISSING_REQUIRED_SECTION"]
    assert any("invalid required_sections" in d.message for d in missing)


# ── combined: multiple invariants at once ──────────────────────────────────────

def test_combined_multiple_diagnostics(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-a"
    repo_root.mkdir()

    repo = _make_repo(
        "repo-a",
        tmp_path,
        provided_artifacts=("missing.json",),
    )
    repos = {"repo-a": repo}
    edges = [DependencyEdge(source="repo-a", target="ghost", required=True, kind="semantic")]
    graph = _make_graph(repos, edges)
    diags = validate_si_invariants(graph)
    codes = {d.code for d in diags}
    assert "SE.ORG.UNRESOLVED_DEPENDENCY" in codes
    assert "SE.ORG.MISSING_PROVIDED_ARTIFACT" in codes

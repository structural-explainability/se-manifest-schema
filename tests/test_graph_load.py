"""Tests for graph/load.py - manifest graph loading."""

from pathlib import Path

from se_manifest_schema.graph.load import (
    _contains_contiguous_parts,
    _dependency_edges_from_items,
    _discover_manifest_paths,
    _is_excluded_manifest_path,
    _string_value,
    load_manifest_graph,
)
from se_manifest_schema.graph.model import DependencyEdge


def _write_manifest(
    directory: Path, content: str, filename: str = "SE_MANIFEST.toml"
) -> Path:
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


def _minimal_manifest_content(name: str = "repo-a", repo_class: str = "core") -> str:
    return f"""
[repository]
name = "{name}"
class = "{repo_class}"
version = "0.1.0"
status = "active"

[layer]
space = "theory"
role = "kernel"
"""


def _schema_content() -> str:
    return """
[class.core]
required_sections = ["repository"]

[section.repository]
allowed_fields = ["name", "class", "version", "status"]
"""


def test_string_value_returns_string() -> None:
    assert _string_value({"key": "val"}, "key") == "val"


def test_string_value_returns_empty_for_missing() -> None:
    assert _string_value({}, "missing") == ""


def test_string_value_returns_empty_for_non_string() -> None:
    assert _string_value({"key": 42}, "key") == ""


def test_contiguous_parts_found() -> None:
    assert _contains_contiguous_parts(("a", "b", "c", "d"), ("b", "c")) is True


def test_contiguous_parts_at_start() -> None:
    assert _contains_contiguous_parts(("a", "b", "c"), ("a", "b")) is True


def test_contiguous_parts_at_end() -> None:
    assert _contains_contiguous_parts(("a", "b", "c"), ("b", "c")) is True


def test_contiguous_parts_not_found() -> None:
    assert _contains_contiguous_parts(("a", "b", "c"), ("a", "c")) is False


def test_contiguous_parts_empty_excluded() -> None:
    assert _contains_contiguous_parts(("a", "b"), ()) is False


def test_contiguous_parts_excluded_longer_than_candidate() -> None:
    assert _contains_contiguous_parts(("a",), ("a", "b")) is False


def test_excluded_by_dir_name(tmp_path: Path) -> None:
    manifest = tmp_path / ".venv" / "SE_MANIFEST.toml"
    manifest.parent.mkdir()
    manifest.touch()
    assert _is_excluded_manifest_path(
        manifest,
        root=tmp_path,
        excluded_dir_names=[".venv"],
        excluded_path_parts=[],
    )


def test_not_excluded_when_no_rules(tmp_path: Path) -> None:
    manifest = tmp_path / "repository" / "SE_MANIFEST.toml"
    manifest.parent.mkdir()
    manifest.touch()
    assert not _is_excluded_manifest_path(
        manifest,
        root=tmp_path,
        excluded_dir_names=[],
        excluded_path_parts=[],
    )


def test_excluded_by_path_parts(tmp_path: Path) -> None:
    manifest = tmp_path / "tests" / "fixtures" / "SE_MANIFEST.toml"
    manifest.parent.mkdir(parents=True)
    manifest.touch()
    assert _is_excluded_manifest_path(
        manifest,
        root=tmp_path,
        excluded_dir_names=[],
        excluded_path_parts=[("tests", "fixtures")],
    )


def test_discover_finds_se_manifest(tmp_path: Path) -> None:
    sub = tmp_path / "repository"
    sub.mkdir()
    (sub / "SE_MANIFEST.toml").write_text("[repository]\nname='x'\n", encoding="utf-8")
    paths = _discover_manifest_paths(tmp_path)
    assert any(p.name == "SE_MANIFEST.toml" for p in paths)


def test_discover_prefers_se_manifest_over_manifest(tmp_path: Path) -> None:
    sub = tmp_path / "repository"
    sub.mkdir()
    (sub / "SE_MANIFEST.toml").write_text("[repository]\nname='a'\n", encoding="utf-8")
    (sub / "MANIFEST.toml").write_text("[repository]\nname='b'\n", encoding="utf-8")
    paths = _discover_manifest_paths(tmp_path)
    names = [p.name for p in paths]
    assert "SE_MANIFEST.toml" in names
    assert "MANIFEST.toml" not in names


def test_discover_finds_manifest_toml_fallback(tmp_path: Path) -> None:
    sub = tmp_path / "repository"
    sub.mkdir()
    (sub / "MANIFEST.toml").write_text("[repository]\nname='b'\n", encoding="utf-8")
    paths = _discover_manifest_paths(tmp_path)
    assert any(p.name == "MANIFEST.toml" for p in paths)


def test_discover_empty_dir(tmp_path: Path) -> None:
    assert _discover_manifest_paths(tmp_path) == []


def test_edges_from_string_items() -> None:
    edges = _dependency_edges_from_items(
        source="repo-a", items=["repo-b", "repo-c"], required=True
    )
    assert len(edges) == 2
    assert all(isinstance(e, DependencyEdge) for e in edges)
    assert edges[0].target == "repo-b"
    assert edges[0].required is True
    assert edges[0].kind == "semantic"


def test_edges_from_dict_items() -> None:
    edges = _dependency_edges_from_items(
        source="repo-a",
        items=[
            {
                "repository": "repo-b",
                "kind": "artifact",
                "version": "1.0",
                "reason": "needs",
            }
        ],
        required=False,
    )
    assert len(edges) == 1
    assert edges[0].target == "repo-b"
    assert edges[0].kind == "artifact"
    assert edges[0].version == "1.0"
    assert edges[0].reason == "needs"
    assert edges[0].required is False


def test_edges_skips_dict_without_repo_key() -> None:
    edges = _dependency_edges_from_items(
        source="repo-a",
        items=[{"kind": "artifact"}],
        required=True,
    )
    assert edges == []


def test_edges_skips_non_string_non_dict() -> None:
    edges = _dependency_edges_from_items(
        source="repo-a",
        items=[42, None, True],
        required=True,
    )
    assert edges == []


def test_edges_from_non_list_returns_empty() -> None:
    edges = _dependency_edges_from_items(
        source="repo-a", items="not-a-list", required=True
    )
    assert edges == []


def test_edges_dict_item_defaults_kind_to_semantic() -> None:
    edges = _dependency_edges_from_items(
        source="a",
        items=[{"repository": "b"}],
        required=True,
    )
    assert edges[0].kind == "semantic"


def test_edges_dict_item_with_non_string_kind_defaults_semantic() -> None:
    edges = _dependency_edges_from_items(
        source="a",
        items=[{"repository": "b", "kind": 99}],
        required=True,
    )
    assert edges[0].kind == "semantic"


def test_load_manifest_graph_empty_root(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")
    graph = load_manifest_graph(root=tmp_path, schema_path=schema_path)
    assert graph.repositories == {}
    assert graph.edges == ()


def test_load_manifest_graph_single_repo(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo-a"
    repo_dir.mkdir()
    _write_manifest(repo_dir, _minimal_manifest_content("repo-a"))

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")

    graph = load_manifest_graph(root=tmp_path, schema_path=schema_path)
    assert "repo-a" in graph.repositories


def test_load_manifest_graph_with_dependencies(tmp_path: Path) -> None:
    content = """
[repository]
name = "repo-a"
class = "core"
version = "0.1.0"
status = "active"

[layer]
space = "theory"
role = "kernel"

[depends]
required = [{repository = "repo-b", kind = "semantic"}]
optional = ["repo-c"]
"""
    repo_dir = tmp_path / "repo-a"
    repo_dir.mkdir()
    _write_manifest(repo_dir, content)

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")

    graph = load_manifest_graph(root=tmp_path, schema_path=schema_path)
    assert len(graph.edges) == 2
    targets = {e.target for e in graph.edges}
    assert "repo-b" in targets
    assert "repo-c" in targets


def test_load_manifest_graph_excludes_dir_names(tmp_path: Path) -> None:
    venv_dir = tmp_path / ".venv" / "some-repo"
    venv_dir.mkdir(parents=True)
    _write_manifest(venv_dir, _minimal_manifest_content("hidden-repo"))

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")

    graph = load_manifest_graph(
        root=tmp_path,
        schema_path=schema_path,
        excluded_dir_names=[".venv"],
    )
    assert "hidden-repo" not in graph.repositories


def test_load_manifest_graph_excludes_path_parts(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "fixtures"
    fixture_dir.mkdir(parents=True)
    _write_manifest(fixture_dir, _minimal_manifest_content("fixture-repo"))

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")

    graph = load_manifest_graph(
        root=tmp_path,
        schema_path=schema_path,
        excluded_path_parts=[("tests", "fixtures")],
    )
    assert "fixture-repo" not in graph.repositories


def test_load_manifest_graph_captures_provided_artifacts(tmp_path: Path) -> None:
    content = """
[repository]
name = "provider"
class = "core"
version = "0.1.0"
status = "active"

[layer]
space = "theory"
role = "kernel"

[provides]
artifacts = ["output/schema.json", "output/report.md"]
"""
    repo_dir = tmp_path / "provider"
    repo_dir.mkdir()
    _write_manifest(repo_dir, content)

    schema_path = tmp_path / "manifest-schema.toml"
    schema_path.write_text(_schema_content(), encoding="utf-8")

    graph = load_manifest_graph(root=tmp_path, schema_path=schema_path)
    repo = graph.repositories["provider"]
    assert "output/schema.json" in repo.provided_artifacts
    assert "output/report.md" in repo.provided_artifacts

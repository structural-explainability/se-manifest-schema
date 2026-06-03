"""Load repository manifests into a manifest graph."""

from collections.abc import Iterable, Sequence
from pathlib import Path
import tomllib
from typing import Any, cast

from se_manifest_schema.graph.model import (
    DependencyEdge,
    GraphRepository,
    ManifestGraph,
)
from se_manifest_schema.load import SUPPORTED_MANIFEST_FILE_NAMES

__all__ = ["load_manifest_graph"]

IGNORED_DIR_NAMES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
}


def load_manifest_graph(
    *,
    root: Path,
    schema_path: Path,
    excluded_dir_names: Iterable[str] = (),
    excluded_path_parts: Iterable[Sequence[str]] = (),
) -> ManifestGraph:
    """Load the manifest graph."""
    resolved_root = root.resolve()

    manifest_paths = [
        path
        for path in _discover_manifest_paths(resolved_root)
        if not _is_excluded_manifest_path(
            path,
            root=resolved_root,
            excluded_dir_names=excluded_dir_names,
            excluded_path_parts=excluded_path_parts,
        )
    ]

    repositories: dict[str, GraphRepository] = {}
    edges: list[DependencyEdge] = []
    manifest_schema: dict[str, Any] = _load_toml(schema_path)

    for manifest_path in manifest_paths:
        manifest = _load_toml(manifest_path)
        repository = _repository_from_manifest(
            manifest_path=manifest_path, manifest=manifest
        )
        repositories[repository.name] = repository
        edges.extend(
            _dependency_edges_from_manifest(repository=repository, manifest=manifest)
        )

    return ManifestGraph(
        repositories=repositories,
        edges=tuple(edges),
        missing_manifest_roots=(),
        manifest_schema=manifest_schema,
    )


def _is_excluded_manifest_path(
    path: Path,
    *,
    root: Path,
    excluded_dir_names: Iterable[str],
    excluded_path_parts: Iterable[Sequence[str]],
) -> bool:
    """Return whether a manifest path is outside the managed graph."""
    relative_parts = path.resolve().relative_to(root.resolve()).parts

    excluded_names = set(excluded_dir_names)
    if any(part in excluded_names for part in relative_parts):
        return True

    return any(
        _contains_contiguous_parts(relative_parts, tuple(parts))
        for parts in excluded_path_parts
    )


def _contains_contiguous_parts(
    candidate_parts: tuple[str, ...],
    excluded_parts: tuple[str, ...],
) -> bool:
    """Return whether candidate_parts contains excluded_parts in order."""
    if not excluded_parts:
        return False

    excluded_length = len(excluded_parts)
    return any(
        candidate_parts[index : index + excluded_length] == excluded_parts
        for index in range(len(candidate_parts) - excluded_length + 1)
    )


def _load_toml(path: Path) -> dict[str, Any]:
    """Load TOML data from a path."""
    with path.open("rb") as file:
        print(f"Loading manifest: {path}")
        return tomllib.load(file)


def _repository_from_manifest(
    *,
    manifest_path: Path,
    manifest: dict[str, Any],
) -> GraphRepository:
    """Build a graph repository from one manifest."""
    repo = cast(dict[str, Any], manifest.get("repository", {}))
    layer = cast(dict[str, Any], manifest.get("layer", {}))
    provides = cast(dict[str, Any], manifest.get("provides", {}))

    artifacts_raw = provides.get("artifacts", [])
    artifacts = tuple(item for item in artifacts_raw if isinstance(item, str))

    return GraphRepository(
        name=_string_value(repo, "name"),
        repo_class=_string_value(repo, "class"),
        layer_space=_string_value(layer, "space"),
        layer_role=_string_value(layer, "role"),
        status=_string_value(repo, "status"),
        root=manifest_path.parent,
        manifest_path=manifest_path,
        manifest=manifest,
        provided_artifacts=artifacts,
    )


def _dependency_edges_from_manifest(
    *,
    repository: GraphRepository,
    manifest: dict[str, Any],
) -> list[DependencyEdge]:
    """Extract dependency edges from one manifest."""
    depends = cast(dict[str, Any], manifest.get("depends", {}))
    edges: list[DependencyEdge] = []

    edges.extend(
        _dependency_edges_from_items(
            source=repository.name,
            items=depends.get("required", []),
            required=True,
        )
    )
    edges.extend(
        _dependency_edges_from_items(
            source=repository.name,
            items=depends.get("optional", []),
            required=False,
        )
    )

    return edges


def _dependency_edges_from_items(
    *,
    source: str,
    items: object,
    required: bool,
) -> list[DependencyEdge]:
    """Extract dependency edges from required or optional dependency items."""
    if not isinstance(items, list):
        return []

    edges: list[DependencyEdge] = []

    for item in cast(list[Any], items):
        if isinstance(item, str):
            edges.append(
                DependencyEdge(
                    source=source,
                    target=item,
                    required=required,
                    kind="semantic",
                )
            )
            continue

        if not isinstance(item, dict):
            continue

        item_typed = cast(dict[str, Any], item)
        target = item_typed.get("repository")
        kind = item_typed.get("kind", "semantic")
        version = item_typed.get("version")
        reason = item_typed.get("reason")

        if not isinstance(target, str) or not target:
            continue

        edges.append(
            DependencyEdge(
                source=source,
                target=target,
                required=required,
                kind=kind if isinstance(kind, str) else "semantic",
                version=version if isinstance(version, str) else None,
                reason=reason if isinstance(reason, str) else None,
            )
        )

    return edges


def _discover_manifest_paths(root: Path) -> list[Path]:
    """Discover supported manifest files under root.

    The canonical manifest filename is preferred when both supported manifest
    filenames appear in the same directory.

    Discovery is intentionally broad. Managed-graph exclusions are applied by
    the caller so discovery remains simple and auditable.
    """
    resolved_root = root.resolve()

    manifest_dirs = {
        path.parent.resolve()
        for filename in SUPPORTED_MANIFEST_FILE_NAMES
        for path in resolved_root.rglob(filename)
        if path.is_file()
    }

    manifest_paths: list[Path] = []
    for manifest_dir in sorted(manifest_dirs):
        for filename in SUPPORTED_MANIFEST_FILE_NAMES:
            candidate = manifest_dir / filename
            if candidate.is_file():
                manifest_paths.append(candidate.resolve())
                break

    return manifest_paths


def _string_value(table: dict[str, Any], key: str) -> str:
    """Return a string value from a TOML table or an empty string."""
    value = table.get(key)
    return value if isinstance(value, str) else ""

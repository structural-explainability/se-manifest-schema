"""Data model for manifest graph verification."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "DependencyEdge",
    "GraphRepository",
    "ManifestGraph",
]


@dataclass(frozen=True)
class DependencyEdge:
    """One declared repository dependency."""

    source: str
    target: str
    required: bool
    kind: str
    version: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class GraphRepository:
    """One repository node in the manifest graph."""

    name: str
    repo_class: str
    layer_space: str
    layer_role: str
    status: str
    root: Path
    manifest_path: Path
    manifest: dict[str, Any]
    provided_artifacts: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ManifestGraph:
    """Resolved manifest graph input."""

    repositories: dict[str, GraphRepository]
    edges: tuple[DependencyEdge, ...]
    missing_manifest_roots: tuple[Path, ...]
    manifest_schema: dict[str, Any]

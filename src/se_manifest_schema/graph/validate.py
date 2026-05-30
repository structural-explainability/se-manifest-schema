"""Validate SI invariants for manifest graph verification."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, cast

from se_manifest_schema.graph.diagnostics import GraphDiagnostic
from se_manifest_schema.graph.model import (
    GraphRepository,
    ManifestGraph,
)

__all__ = ["validate_si_invariants"]


def validate_si_invariants(graph: ManifestGraph) -> list[GraphDiagnostic]:
    """Validate SI01, SI02, SI03, and SI04."""
    diagnostics: list[GraphDiagnostic] = []

    diagnostics.extend(_validate_si01_required_semantic_graph_acyclic(graph))
    diagnostics.extend(_validate_si02_dependencies_resolve(graph))
    diagnostics.extend(_validate_si03_provides_are_real(graph))
    diagnostics.extend(_validate_si04_class_registry_satisfied(graph))

    return diagnostics


def _validate_si01_required_semantic_graph_acyclic(
    graph: ManifestGraph,
) -> list[GraphDiagnostic]:
    """Validate SI01: required semantic dependency graph is acyclic."""
    adjacency: dict[str, list[str]] = defaultdict(list)

    for edge in graph.edges:
        if edge.required and edge.kind == "semantic":
            adjacency[edge.source].append(edge.target)

    return _cycle_diagnostics(adjacency)


def _cycle_diagnostics(adjacency: dict[str, list[str]]) -> list[GraphDiagnostic]:
    """Return diagnostics for cycles in an adjacency list."""
    diagnostics: list[GraphDiagnostic] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return

        if node in visiting:
            cycle = _cycle_path(stack=stack, node=node)
            diagnostics.append(
                GraphDiagnostic(
                    code="SE.ORG.DEPENDENCY_CYCLE",
                    repo=node,
                    message=f"required semantic dependency cycle: {' -> '.join(cycle)}",
                )
            )
            return

        visiting.add(node)
        stack.append(node)

        for target in adjacency.get(node, []):
            visit(target)

        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(adjacency):
        visit(node)

    return diagnostics


def _cycle_path(*, stack: list[str], node: str) -> list[str]:
    """Return the visible cycle path for a repeated node."""
    if node not in stack:
        return [node, node]

    start = stack.index(node)
    return [*stack[start:], node]


def _validate_si02_dependencies_resolve(graph: ManifestGraph) -> list[GraphDiagnostic]:
    """Validate SI02: all declared dependencies resolve."""
    diagnostics: list[GraphDiagnostic] = []

    for edge in graph.edges:
        if edge.target not in graph.repositories:
            diagnostics.append(
                GraphDiagnostic(
                    code="SE.ORG.UNRESOLVED_DEPENDENCY",
                    repo=edge.source,
                    message=(
                        f"dependency target '{edge.target}' does not resolve "
                        f"(kind={edge.kind})"
                    ),
                )
            )

    return diagnostics


def _validate_si03_provides_are_real(graph: ManifestGraph) -> list[GraphDiagnostic]:
    """Validate SI03: provided artifacts exist."""
    diagnostics: list[GraphDiagnostic] = []

    for repository in graph.repositories.values():
        diagnostics.extend(_provided_artifact_diagnostics(repository))

    return diagnostics


def _provided_artifact_diagnostics(
    repository: GraphRepository,
) -> list[GraphDiagnostic]:
    """Return diagnostics for missing provided artifacts in one repository."""
    diagnostics: list[GraphDiagnostic] = []

    for artifact in repository.provided_artifacts:
        artifact_path = repository.root / artifact
        if artifact_path.exists():
            continue

        diagnostics.append(
            GraphDiagnostic(
                code="SE.ORG.MISSING_PROVIDED_ARTIFACT",
                repo=repository.name,
                path=str(artifact_path),
                message=f"provided artifact '{artifact}' does not exist",
            )
        )

    return diagnostics


def _validate_si04_class_registry_satisfied(
    graph: ManifestGraph,
) -> list[GraphDiagnostic]:
    """Validate SI04: class registry requirements are satisfied."""
    diagnostics: list[GraphDiagnostic] = []
    class_registry = cast(dict[str, Any], graph.manifest_schema.get("class", {}))

    for repository in graph.repositories.values():
        diagnostics.extend(
            _class_registry_diagnostics(
                repository=repository,
                class_registry=class_registry,
            )
        )

    return diagnostics


def _class_registry_diagnostics(
    *,
    repository: GraphRepository,
    class_registry: dict[str, Any],
) -> list[GraphDiagnostic]:
    """Return class registry diagnostics for one repository."""
    class_def = class_registry.get(repository.repo_class)

    if not isinstance(class_def, dict):
        return [
            GraphDiagnostic(
                code="SE.ORG.MISSING_REQUIRED_SECTION",
                repo=repository.name,
                path=str(repository.manifest_path),
                message=f"unknown manifest class '{repository.repo_class}'",
            )
        ]

    class_def_typed = cast(dict[str, Any], class_def)
    required_sections = class_def_typed.get("required_sections", [])

    if not isinstance(required_sections, list):
        return [
            GraphDiagnostic(
                code="SE.ORG.MISSING_REQUIRED_SECTION",
                repo=repository.name,
                path=str(repository.manifest_path),
                message=f"class '{repository.repo_class}' has invalid required_sections",
            )
        ]

    required_sections = cast(list[Any], required_sections)
    diagnostics: list[GraphDiagnostic] = []

    for section in required_sections:
        if not isinstance(section, str):
            continue

        if section in repository.manifest:
            continue

        diagnostics.append(
            GraphDiagnostic(
                code="SE.ORG.MISSING_REQUIRED_SECTION",
                repo=repository.name,
                path=str(repository.manifest_path),
                message=(
                    f"manifest class '{repository.repo_class}' requires "
                    f"section '{section}'"
                ),
            )
        )

    return diagnostics

"""Report rendering for manifest graph verification."""

from se_manifest_schema.graph.diagnostics import GraphDiagnostic
from se_manifest_schema.graph.model import ManifestGraph

__all__ = ["render_markdown_report"]


def render_markdown_report(
    *,
    graph: ManifestGraph,
    diagnostics: list[GraphDiagnostic],
) -> str:
    """Render a Markdown manifest graph report."""
    lines = [
        "# Manifest Graph Report",
        "",
        "## Summary",
        "",
        f"- Repositories: {len(graph.repositories)}",
        f"- Dependencies: {len(graph.edges)}",
        f"- Diagnostics: {len(diagnostics)}",
        "",
        "## Diagnostics",
        "",
    ]

    if diagnostics:
        lines.extend(f"- {diagnostic.render()}" for diagnostic in diagnostics)
    else:
        lines.append("- No diagnostics.")

    lines.extend(
        [
            "",
            "## Repositories",
            "",
        ]
    )

    for name in sorted(graph.repositories):
        repository = graph.repositories[name]
        lines.append(
            "-"
            f"{repository.name} "
            f"(class={repository.repo_class}, role={repository.layer_role})"
        )

    lines.extend(
        [
            "",
            "## Dependencies",
            "",
        ]
    )

    if graph.edges:
        for edge in graph.edges:
            required = "required" if edge.required else "optional"
            lines.append(
                f"-{edge.source} -> {edge.target} ({required}, kind={edge.kind})"
            )
    else:
        lines.append("- No dependencies.")

    lines.append("")
    return "\n".join(lines)

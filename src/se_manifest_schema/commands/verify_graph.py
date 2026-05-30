"""Verify the manifest dependency graph."""

from pathlib import Path

from se_manifest_schema.graph.load import load_manifest_graph
from se_manifest_schema.graph.report import render_markdown_report
from se_manifest_schema.graph.validate import validate_si_invariants

__all__ = ["run"]

SCHEMA_REPO_NAME = "se-manifest-schema"
DEFAULT_SCHEMA_FILE = "manifest-schema.toml"
DEFAULT_REPORT_PATH = Path("data/reports/org-graph-report.md")

EXCLUDED_MANIFEST_DIR_NAMES = [
    ".lake",
    ".venv",
    "site-packages",
]

EXCLUDED_MANIFEST_PATH_PARTS = [
    ("tests", "fixtures"),
]

EXCLUDED_MANIFEST_PATHS = [
    Path(".lake"),
    Path(".lake/packages"),
]


def run(
    *,
    root: Path | None,
    schema_path: Path | None,
    report_path: Path | None,
) -> int:
    """Run manifest graph verification."""
    working_dir = Path.cwd()
    schema_repo = _find_schema_repo(working_dir)

    resolved_root = _resolve_root(
        root=root,
        working_dir=working_dir,
        schema_repo=schema_repo,
    )
    resolved_schema_path = _resolve_schema_path(
        schema_path=schema_path,
        working_dir=working_dir,
        schema_repo=schema_repo,
    )
    resolved_report_path = _resolve_report_path(
        report_path=report_path,
        working_dir=working_dir,
        schema_repo=schema_repo,
    )

    graph = load_manifest_graph(
        root=resolved_root,
        schema_path=resolved_schema_path,
        excluded_dir_names=EXCLUDED_MANIFEST_DIR_NAMES,
        excluded_path_parts=EXCLUDED_MANIFEST_PATH_PARTS,
    )
    diagnostics = validate_si_invariants(graph)
    report = render_markdown_report(graph=graph, diagnostics=diagnostics)

    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(report, encoding="utf-8")

    if diagnostics:
        print("[verify-graph] FAILED")
        print(f"[verify-graph] root: {resolved_root}")
        print(f"[verify-graph] schema: {resolved_schema_path}")
        for diagnostic in diagnostics:
            print(f"- {diagnostic.render()}")
        print(f"[verify-graph] report: {resolved_report_path}")
        return 1

    print("[verify-graph] PASSED")
    print(f"[verify-graph] root: {resolved_root}")
    print(f"[verify-graph] schema: {resolved_schema_path}")
    print(f"[verify-graph] report: {resolved_report_path}")
    return 0


def _resolve_root(
    *,
    root: Path | None,
    working_dir: Path,
    schema_repo: Path,
) -> Path:
    """Resolve graph scan root."""
    if root is not None:
        return _resolve_path(
            root,
            working_dir=working_dir,
            schema_repo=schema_repo,
        )

    if _looks_like_schema_repo(working_dir):
        return schema_repo.parent.resolve()

    return working_dir.resolve()


def _resolve_schema_path(
    *,
    schema_path: Path | None,
    working_dir: Path,
    schema_repo: Path,
) -> Path:
    """Resolve manifest-schema.toml path."""
    if schema_path is None:
        return (schema_repo / DEFAULT_SCHEMA_FILE).resolve()

    return _resolve_path(
        schema_path,
        working_dir=working_dir,
        schema_repo=schema_repo,
    )


def _resolve_report_path(
    *,
    report_path: Path | None,
    working_dir: Path,
    schema_repo: Path,
) -> Path:
    """Resolve Markdown report path."""
    if report_path is None:
        return (schema_repo / DEFAULT_REPORT_PATH).resolve()

    return _resolve_path(
        report_path,
        working_dir=working_dir,
        schema_repo=schema_repo,
    )


def _find_schema_repo(working_dir: Path) -> Path:
    """Find the se-manifest-schema repository."""
    current = working_dir.resolve()

    while True:
        if _looks_like_schema_repo(current):
            return current

        if current == current.parent:
            break

        current = current.parent

    candidate = working_dir / SCHEMA_REPO_NAME
    if _looks_like_schema_repo(candidate):
        return candidate.resolve()

    return working_dir.resolve()


def _looks_like_schema_repo(path: Path) -> bool:
    """Return whether path looks like the se-manifest-schema repository."""
    return (
        path.name == SCHEMA_REPO_NAME
        and (path / DEFAULT_SCHEMA_FILE).is_file()
        and (path / "SE_MANIFEST.toml").is_file()
    )


def _resolve_path(
    path: Path,
    *,
    working_dir: Path,
    schema_repo: Path,
) -> Path:
    """Resolve a user-provided path.

    Resolution order:

    - absolute path
    - relative to current working directory
    - relative to the se-manifest-schema repository
    - relative to current working directory as an unresolved fallback
    """
    if path.is_absolute():
        return path.resolve()

    working_dir_candidate = (working_dir / path).resolve()
    if working_dir_candidate.exists():
        return working_dir_candidate

    schema_repo_candidate = (schema_repo / path).resolve()
    if schema_repo_candidate.exists():
        return schema_repo_candidate

    return working_dir_candidate

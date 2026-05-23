"""load.py - Loading and parsing."""

from importlib.resources import files
from pathlib import Path
import shutil
import subprocess
import tomllib
from typing import Any, Final

__all__ = [
    "find_manifest_path",
    "get_git_tag",
    "load_manifest",
    "load_schema",
    "load_toml",
    "packaged_schema_text",
    "repo_root_schema_path",
    "schema_text",
]

SCHEMA_FILENAME: Final[str] = "manifest-schema.toml"
PACKAGE_NAME: Final[str] = "se_manifest_schema"

CANONICAL_MANIFEST_FILE_NAME: Final[str] = "SE_MANIFEST.toml"
ALTERNATE_MANIFEST_FILE_NAME: Final[str] = "MANIFEST.toml"
SUPPORTED_MANIFEST_FILE_NAMES: Final[tuple[str, ...]] = (
    CANONICAL_MANIFEST_FILE_NAME,
    ALTERNATE_MANIFEST_FILE_NAME,
)


def find_manifest_path(start: Path | None = None) -> Path:
    """Find the supported repository manifest path in the given directory.

    The canonical name is preferred when both files are present.
    """
    root = start if start is not None else Path.cwd()

    for filename in SUPPORTED_MANIFEST_FILE_NAMES:
        candidate = root / filename
        if candidate.is_file():
            return candidate

    supported = ", ".join(SUPPORTED_MANIFEST_FILE_NAMES)
    raise FileNotFoundError(
        f"No supported manifest found. Expected one of: {supported}"
    )


def get_git_tag() -> str:
    """Return the current git tag (exact match required)."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable not found on PATH")
    try:
        return (
            subprocess.check_output(  # noqa: S603
                [git, "describe", "--tags", "--exact-match"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Repository is not on a tagged commit") from exc


def get_repo_version(manifest: dict[str, Any]) -> str:
    """Extract the repo version from the manifest."""
    repo: Any = manifest.get("repo")

    if not isinstance(repo, dict):
        raise ValueError("Manifest missing 'repo' section")

    repo_typed: dict[str, Any] = repo  # type: ignore[assignment]
    version: Any = repo_typed.get("version")

    if not isinstance(version, str):
        raise ValueError("Manifest 'repo' section missing 'version' string")

    return version


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load manifest from the given path or supported repo-root filename."""
    if path is not None and not path.is_file():
        supported = ", ".join(SUPPORTED_MANIFEST_FILE_NAMES)
        raise FileNotFoundError(
            f"Manifest not found: {path}. Supported names: {supported}"
        )
    target = path if path is not None else find_manifest_path()
    return load_toml(target)


def load_schema() -> dict[str, Any]:
    """Load manifest-schema.toml from source checkout or packaged resource."""
    return tomllib.loads(schema_text())


def load_toml(path: Path) -> dict[str, Any]:
    """Load and return TOML data from the specified path."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def packaged_schema_text() -> str:
    """Load the schema embedded in the installed package."""
    schema = files(PACKAGE_NAME).joinpath(SCHEMA_FILENAME)
    return schema.read_text(encoding="utf-8")


def repo_root_schema_path(start: Path | None = None) -> Path | None:
    """Return the repo-root schema path when running from a source checkout."""
    current = (start or Path.cwd()).resolve()

    for candidate_root in (current, *current.parents):
        candidate = candidate_root / SCHEMA_FILENAME
        pyproject = candidate_root / "pyproject.toml"
        src_package = candidate_root / "src" / PACKAGE_NAME

        if candidate.is_file() and pyproject.is_file() and src_package.is_dir():
            return candidate

    return None


def schema_text() -> str:
    """Load canonical schema text from source checkout or packaged resource."""
    root_schema = repo_root_schema_path()

    if root_schema is not None:
        return root_schema.read_text(encoding="utf-8")

    return packaged_schema_text()

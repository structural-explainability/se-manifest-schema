"""load.py - Loading and parsing for se-manifest-schema.

Owns:
  - load_toml()              - read any TOML file
  - load_schema()            - read canonical schema
  - load_manifest()          - read SE_MANIFEST.toml
  - repo_root_schema_path()  - find schema source of truth
  - packaged_schema_text()   - read packaged schema artifact
  - schema_text()            - read schema from source or package
  - get_git_tag()            - read current exact git tag
"""

from importlib.resources import files
from pathlib import Path
import shutil
import subprocess
import tomllib
from typing import Any, Final, cast

SCHEMA_FILENAME: Final[str] = "manifest-schema.toml"
PACKAGE_NAME: Final[str] = "se_manifest_schema"
MANIFEST_FILE_NAME: Final[str] = "SE_MANIFEST.toml"


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


def packaged_schema_text() -> str:
    """Load the schema embedded in the installed package."""
    schema = files(PACKAGE_NAME).joinpath(SCHEMA_FILENAME)
    return schema.read_text(encoding="utf-8")


def schema_text() -> str:
    """Load canonical schema text from source checkout or packaged resource."""
    root_schema = repo_root_schema_path()

    if root_schema is not None:
        return root_schema.read_text(encoding="utf-8")

    return packaged_schema_text()


def load_toml(path: Path) -> dict[str, Any]:
    """Load and return TOML data from the specified path."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_schema() -> dict[str, Any]:
    """Load manifest-schema.toml from source checkout or packaged resource."""
    return tomllib.loads(schema_text())


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load manifest from the given path or repo root."""
    target = path if path is not None else Path(MANIFEST_FILE_NAME)
    if not target.exists():
        raise FileNotFoundError(f"{MANIFEST_FILE_NAME} not found: {target}")
    return load_toml(target)


def get_repo_version(manifest: dict[str, Any]) -> str:
    """Extract and validate repo.version from manifest."""
    repo = manifest.get("repo")
    if not isinstance(repo, dict):
        raise ValueError(f"{MANIFEST_FILE_NAME} missing or invalid [repo] section")
    typed: dict[str, object] = cast(dict[str, object], repo)
    version = typed.get("version")
    if not isinstance(version, str):
        raise ValueError(f"{MANIFEST_FILE_NAME} missing or invalid repo.version")
    return version


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

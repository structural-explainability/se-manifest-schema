"""check_version.py - Version consistency check.

CITATION.cff is the version source of truth, updated manually before release.
This module CHECKS that other version expressions agree with it. It never
writes any file.

Checked for agreement with CITATION.cff:
  - pyproject.toml fallback-version
  - the current git tag (only when require_tag=True)

Reads but never modifies:
  - CITATION.cff      (the source of truth, updated manually at release)
  - pyproject.toml    (fallback-version is compared, not rewritten)

Does not touch:
  - manifest-schema.toml
  - SE_MANIFEST.toml
  - MANIFEST.toml
"""

from pathlib import Path
import re
import tomllib

from se_manifest_schema.load import get_git_tag

__all__ = [
    "get_version_from_citation",
    "get_fallback_version",
    "run",
]

EXIT_OK = 0
EXIT_MISMATCH = 1

# WHY: CITATION.cff is YAML, but only one flat top-level scalar is needed
# (`version:`). Reading that single line with the stdlib keeps this repo at
# zero runtime dependencies; a full YAML parser is not warranted for one field.
# OBS: CITATION.cff is this repo's own file with a known shape, so a constrained
# line read is safe here even though hand-parsing arbitrary YAML would not be.
_CFF_VERSION_LINE = re.compile(
    r"""^\s*version\s*:\s*["']?(?P<version>[^"'\s#]+)["']?\s*(?:#.*)?$"""
)


def get_fallback_version(path: Path | None = None) -> str:
    """Read fallback-version from pyproject.toml [tool.hatch.version].

    Args:
        path: Path to pyproject.toml. Defaults to ./pyproject.toml.

    Returns:
        The declared fallback-version string.

    Raises:
        FileNotFoundError: If pyproject.toml does not exist.
        ValueError: If fallback-version is missing or not a string.
    """
    target = path if path is not None else Path("pyproject.toml")
    if not target.is_file():
        raise FileNotFoundError("pyproject.toml not found")

    data = tomllib.loads(target.read_text(encoding="utf-8"))
    version = (
        data.get("tool", {}).get("hatch", {}).get("version", {}).get("fallback-version")
    )
    if not isinstance(version, str):
        raise ValueError("pyproject.toml missing [tool.hatch.version] fallback-version")
    return version


def get_version_from_citation(path: Path | None = None) -> str:
    """Read the canonical version from CITATION.cff.

    Args:
        path: Path to CITATION.cff. Defaults to ./CITATION.cff.

    Returns:
        The declared version string.

    Raises:
        FileNotFoundError: If CITATION.cff does not exist.
        ValueError: If no top-level version field is found.
    """
    target = path if path is not None else Path("CITATION.cff")
    if not target.is_file():
        raise FileNotFoundError("CITATION.cff not found")

    for line in target.read_text(encoding="utf-8").splitlines():
        match = _CFF_VERSION_LINE.match(line)
        if match is not None:
            return match.group("version")

    raise ValueError("CITATION.cff missing a top-level 'version' field")


def run(*, require_tag: bool = False) -> int:
    """Check that all version expressions agree with CITATION.cff.

    Compares CITATION.cff against pyproject.toml fallback-version, and (when
    require_tag is True) against the current git tag. Reports every mismatch
    and returns a nonzero exit code if any are found. Writes nothing.

    Args:
        require_tag: Also require the version to match the current git tag.

    Returns:
        EXIT_OK (0) when all checked versions agree, EXIT_MISMATCH (1) otherwise.
    """
    canonical = get_version_from_citation()
    failures: list[str] = []

    fallback = get_fallback_version()
    if fallback != canonical:
        failures.append(
            f"pyproject.toml fallback-version {fallback!r} != "
            f"CITATION.cff version {canonical!r}"
        )

    if require_tag:
        tag = get_git_tag()
        normalized = tag[1:] if tag.startswith("v") else tag
        if normalized != canonical:
            failures.append(f"git tag {tag!r} != CITATION.cff version {canonical!r}")

    if failures:
        for message in failures:
            print(f"[check-version] MISMATCH: {message}")  # noqa: T201
        print(  # noqa: T201
            "[check-version] CITATION.cff is the source of truth; "
            "update the others to match."
        )
        return EXIT_MISMATCH

    if require_tag:
        print(  # noqa: T201
            "[check-version] OK: CITATION.cff, pyproject.toml, "
            f"and git tag agree at {canonical}"
        )
    else:
        print(  # noqa: T201
            f"[check-version] OK: CITATION.cff and pyproject.toml agree at {canonical}"
        )

    return EXIT_OK

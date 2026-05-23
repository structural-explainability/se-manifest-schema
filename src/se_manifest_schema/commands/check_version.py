"""src/se_manifest_schema/commands/check_version.py.

Check that CITATION.cff and pyproject.toml fallback-version agree.
"""

from se_manifest_schema.check_version import run as check_version_run

__all__ = ["run"]


def run(*, require_tag: bool = False) -> int:
    """Check that all version expressions agree with CITATION.cff.

    CITATION.cff is the version source of truth; update it manually before
    running this command. Compares pyproject.toml fallback-version (and, when
    require_tag is True, the current git tag) against it. Writes nothing.

    Args:
        require_tag: Also require the version to match the current git tag.

    Returns:
        0 when all checked versions agree, 1 otherwise.
    """
    try:
        return check_version_run(require_tag=require_tag)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}")  # noqa: T201
        return 1

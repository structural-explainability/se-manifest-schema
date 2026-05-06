"""src/se_manifest_schema/commands/sync_version.py.

Sync CITATION.cff version to pyproject.toml fallback-version.
This repo only; never called automatically as a side effect of validate.
"""

from se_manifest_schema.sync import sync_all


def run() -> int:
    """Sync pyproject.toml fallback-version from CITATION.cff version.

    CITATION.cff is the version source of truth.
    Update it manually before running this command.

    Returns:
        0 on success, 1 on failure.
    """
    try:
        sync_all()
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")  # noqa: T201
        return 1

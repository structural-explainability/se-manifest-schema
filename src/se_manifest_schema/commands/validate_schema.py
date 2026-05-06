"""src/se_manifest_schema/commands/validate_schema.py.

Validate manifest-schema.toml internal consistency.
This repo only; not meaningful in downstream repos.
"""

import tomllib
from typing import cast

from se_manifest_schema.load import repo_root_schema_path
from se_manifest_schema.types.manifest_schema import ManifestSchemaData
from se_manifest_schema.validate_contract import validate_tag
from se_manifest_schema.validate_schema import validate_schema_internal


def run(
    *,
    strict: bool = False,
    require_tag: bool = False,
) -> int:
    """Validate manifest-schema.toml internal consistency.

    Checks that all sections referenced in class definitions exist,
    all allowed_fields have field definitions,
    and all field types are from the allowed set.

    Args:
        strict: Treat warnings as errors.
        require_tag: Require CITATION.cff version to match current git tag.

    Returns:
        0 on success, 1 on failure.
    """
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = repo_root_schema_path()
    if schema_path is None:
        print("ERROR: manifest-schema.toml not found in schema repository checkout")  # noqa: T201
        return 1

    schema = tomllib.loads(schema_path.read_text(encoding="utf-8"))

    print("[validate-schema] manifest-schema.toml")  # noqa: T201

    if require_tag:
        errors.extend(validate_tag({}))

    errors.extend(validate_schema_internal(cast(ManifestSchemaData, schema)))

    for e in errors:
        print(f"ERROR: {e}")  # noqa: T201
    for w in warnings:
        print(f"WARNING: {w}")  # noqa: T201

    if errors:
        return 1
    if strict and warnings:
        return 1

    print("Schema internal validation passed.")  # noqa: T201
    return 0

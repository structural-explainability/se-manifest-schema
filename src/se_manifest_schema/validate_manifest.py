"""validate_manifest.py - Validates repository manifests against manifest-schema.toml.

Imported by consumers to validate their own repository manifest.

Does not know about git tags or version alignment; those are repo-local concerns.

Checks:
  - required top-level fields (schema, schema_url)
  - optional manifest filename, when provided
  - required sections for declared class are present
  - forbidden sections for declared class are absent
  - no unknown sections, if require_known_sections_only is set
  - no unknown fields within sections, if require_known_fields_only is set
  - required fields within sections are present
  - known contract roles
  - contract-class role and authority rules
"""

from typing import Any, cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData

__all_ = ["validate_manifest"]


def validate_manifest(
    manifest: dict[str, Any],
    schema: ManifestSchemaData,
    manifest_filename: str | None = None,
) -> list[str]:
    """Validate a manifest dict against the schema.

    Args:
        manifest: Parsed MANIFEST.toml or SE_MANIFEST.toml content.
        schema: Parsed manifest-schema.toml content.
        manifest_filename: Optional manifest filename to validate against
            schema manifest filename rules.

    Returns:
        List of error strings. Empty list means valid.
    """
    errors: list[str] = []
    rules = _get_validation_rules(schema)

    _validate_manifest_filename(
        schema=schema,
        manifest_filename=manifest_filename,
        errors=errors,
    )

    # --- top-level identity ---
    manifest_section = schema.get("manifest")
    identity: dict[str, object] = {}
    if isinstance(manifest_section, dict):
        identity_raw = manifest_section.get("identity")
        if isinstance(identity_raw, dict):
            identity = identity_raw

    schema_required = identity.get("schema_required")
    if isinstance(schema_required, bool) and schema_required:
        schema_val = manifest.get("schema")
        allowed_raw = identity.get("schema_allowed")
        allowed: list[str] = (
            cast(list[str], allowed_raw) if isinstance(allowed_raw, list) else []
        )
        if schema_val not in allowed:
            errors.append(
                f"manifest.schema: '{schema_val}' not in allowed values {allowed}"
            )

    schema_url_required = identity.get("schema_url_required")
    if (
        isinstance(schema_url_required, bool)
        and schema_url_required
        and not manifest.get("schema_url")
    ):
        errors.append("manifest.schema_url: required but missing")

    # --- repo class ---
    repo = manifest.get("repo")
    if not isinstance(repo, dict):
        errors.append("manifest missing required [repo] section")
        return errors

    typed_repo = cast(dict[str, object], repo)
    class_name = typed_repo.get("class")
    if not isinstance(class_name, str):
        errors.append("[repo].class: required string field missing")
        return errors

    repo_name = typed_repo.get("name")
    if not isinstance(repo_name, str):
        errors.append("[repo].name: required string field missing")
        return errors

    class_def = _get_class_def(schema, class_name)
    if class_def is None:
        errors.append(f"[repo].class: unknown class '{class_name}'")
        return errors

    known_sections = set(schema.get("section", {}).keys())
    manifest_sections = {k for k in manifest if isinstance(manifest.get(k), dict)}

    # --- unknown sections ---
    if rules.get("require_known_sections_only"):
        for section in manifest_sections:
            if section not in known_sections:
                errors.append(f"unknown section '[{section}]'")

    # --- required sections ---
    for section in class_def.get("required_sections", []):
        if section not in manifest:
            errors.append(
                f"class '{class_name}' requires section '[{section}]' but it is missing"
            )

    # --- forbidden sections ---
    for section in class_def.get("forbidden_sections", []):
        if section in manifest:
            errors.append(
                f"class '{class_name}' forbids section '[{section}]' but it is present"
            )

    # --- fields within sections ---
    for section_name in manifest_sections:
        section_def = _get_section_def(schema, section_name)
        if section_def is None:
            continue
        section_data = manifest.get(section_name, {})
        if not isinstance(section_data, dict):
            continue

        allowed_fields = section_def.get("allowed_fields", [])
        allowed_field_names = {
            field for field in allowed_fields if isinstance(field, str)
        }

        # unknown fields
        if rules.get("require_known_fields_only"):
            section_data_typed = cast(dict[str, object], section_data)
            for field_name in section_data_typed:
                if field_name not in allowed_field_names:
                    errors.append(f"[{section_name}].{field_name}: unknown field")

        # required fields
        for field_name in allowed_field_names:
            field_def = _get_field_def(schema, section_name, field_name)
            if field_def is None:
                continue
            if field_def.get("required") and field_name not in section_data:
                errors.append(f"[{section_name}].{field_name}: required field missing")

        _validate_field_constraints(
            schema=schema,
            section_name=section_name,
            section_data=cast(dict[str, Any], section_data),
            errors=errors,
        )

    _validate_contract_rules(
        schema=schema,
        manifest=manifest,
        class_name=class_name,
        repo_name=repo_name,
        errors=errors,
    )

    return errors


def _get_allowed_contract_roles(schema: ManifestSchemaData) -> set[str]:
    """Return allowed contract roles from the schema."""
    allowed = schema.get("contract_roles", {}).get("allowed", [])
    return set(allowed)


def _get_contract_validation_rules(schema: ManifestSchemaData) -> dict[str, Any]:
    """Extract contract-specific validation rules from schema."""
    validation = _get_validation_rules(schema)
    value = validation.get("contract", {})
    return cast(dict[str, Any], value)


def _get_class_def(
    schema: ManifestSchemaData, class_name: str
) -> dict[str, Any] | None:
    """Return class definition for the given class name, or None."""
    value = schema.get("class", {}).get(class_name)
    if value is None:
        return None
    return cast(dict[str, Any], value)


def _get_section_def(
    schema: ManifestSchemaData, section_name: str
) -> dict[str, Any] | None:
    """Return section definition for the given section name, or None."""
    sections = schema.get("section", {})
    value = sections.get(section_name)
    if not isinstance(value, dict):
        return None
    return cast(dict[str, Any], value)


def _get_field_def(
    schema: ManifestSchemaData,
    section_name: str,
    field_name: str,
) -> dict[str, Any] | None:
    """Return field definition for section.field, or None."""
    field_def = schema.get("field", {}).get(section_name, {}).get(field_name)
    if field_def is None:
        return None
    return cast(dict[str, Any], field_def)


def _get_validation_rules(schema: ManifestSchemaData) -> dict[str, Any]:
    """Extract validation rules from schema."""
    value = schema.get("validation", {})
    return cast(dict[str, Any], value)


def _validate_manifest_filename(
    *,
    schema: ManifestSchemaData,
    manifest_filename: str | None,
    errors: list[str],
) -> None:
    """Validate manifest filename when a filename is provided."""
    if manifest_filename is None:
        return

    validation = _get_validation_rules(schema)
    manifest_schema = schema.get("manifest", {})

    if validation.get("require_manifest_filename_allowed"):
        allowed = manifest_schema.get("allowed_filenames", [])
        allowed_names = set(allowed)
        if manifest_filename not in allowed_names:
            errors.append(
                f"manifest filename '{manifest_filename}' not in allowed values "
                f"{sorted(allowed_names)}"
            )
        return

    if validation.get("require_manifest_filename_exact"):
        expected = manifest_schema.get("filename")
        if isinstance(expected, str) and manifest_filename != expected:
            errors.append(
                f"manifest filename '{manifest_filename}' does not match "
                f"required filename '{expected}'"
            )


def _validate_field_constraints(
    *,
    schema: ManifestSchemaData,
    section_name: str,
    section_data: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate supported field constraints."""
    for field_name, value in section_data.items():
        field_def = _get_field_def(schema, section_name, field_name)
        if field_def is None:
            continue

        constraints = field_def.get("constraints", [])
        if not isinstance(constraints, list):
            continue

        if "known-contract-role" in constraints:
            allowed_roles = _get_allowed_contract_roles(schema)
            if value not in allowed_roles:
                errors.append(
                    f"[{section_name}].{field_name}: '{value}' not in "
                    f"allowed contract roles {sorted(allowed_roles)}"
                )


def _validate_contract_rules(
    *,
    schema: ManifestSchemaData,
    manifest: dict[str, Any],
    class_name: str,
    repo_name: str,
    errors: list[str],
) -> None:
    """Validate contract-class rules declared by the schema."""
    rules = _get_contract_validation_rules(schema)
    if class_name != "contract":
        return

    contract = manifest.get("contract", {})
    if not isinstance(contract, dict):
        return

    contract_data = cast(dict[str, Any], contract)
    contract_role = contract_data.get("contract_role")
    contract_authority = contract_data.get("contract_authority")
    contract_version = contract_data.get("contract_version")
    consumes_contract_from = contract_data.get("consumes_contract_from")

    if rules.get("contract_role_required_for_contract_class") and not contract_role:
        errors.append("[contract].contract_role: required for class 'contract'")

    if (
        rules.get("contract_authority_required_for_contract_class")
        and not contract_authority
    ):
        errors.append("[contract].contract_authority: required for class 'contract'")

    if (
        rules.get("contract_version_required_for_contract_class")
        and not contract_version
    ):
        errors.append("[contract].contract_version: required for class 'contract'")

    if rules.get("contract_role_must_be_known"):
        allowed_roles = _get_allowed_contract_roles(schema)
        if contract_role not in allowed_roles:
            errors.append(
                f"[contract].contract_role: '{contract_role}' not in "
                f"allowed contract roles {sorted(allowed_roles)}"
            )

    if (
        rules.get("contract_authority_must_equal_self")
        and contract_authority != repo_name
    ):
        errors.append(
            f"[contract].contract_authority: must equal [repo].name ('{repo_name}')"
        )

    if (
        rules.get("authority_role_must_not_consume_contract")
        and contract_role == "authority"
        and consumes_contract_from
    ):
        errors.append(
            "[contract].consumes_contract_from: must be absent for "
            "contract_role 'authority'"
        )

    if (
        rules.get("domain_contract_role_must_consume_contract")
        and contract_role == "domain-contract"
        and not consumes_contract_from
    ):
        errors.append(
            "[contract].consumes_contract_from: required for "
            "contract_role 'domain-contract'"
        )

    if (
        rules.get("domain_contract_must_not_consume_self")
        and contract_role == "domain-contract"
        and consumes_contract_from == repo_name
    ):
        errors.append(
            "[contract].consumes_contract_from: domain contract must not consume itself"
        )

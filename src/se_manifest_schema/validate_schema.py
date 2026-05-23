"""validate_schema.py - Validate manifest-schema.toml internal consistency."""

from typing import Any, cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData

ALLOWED_FIELD_TYPES = {"string", "boolean", "list[string]"}
REQUIRED_CONTRACT_ROLES = {"authority", "domain-contract"}
REQUIRED_MANIFEST_FILENAMES = ("SE_MANIFEST.toml", "MANIFEST.toml")

__all__ = ["validate_schema_internal"]


def validate_schema_internal(schema: ManifestSchemaData) -> list[str]:
    """Validate internal consistency of manifest-schema.toml."""
    errors: list[str] = []

    sections = cast(dict[str, Any], schema.get("section", {}))
    fields = cast(dict[str, Any], schema.get("field", {}))
    classes = cast(dict[str, Any], schema.get("class", {}))
    manifest = cast(dict[str, Any], schema.get("manifest", {}))
    validation = cast(dict[str, Any], schema.get("validation", {}))
    contract_roles = cast(dict[str, Any], schema.get("contract_roles", {}))

    for class_name, class_def in classes.items():
        if not isinstance(class_def, dict):
            continue

        class_def_typed = cast(dict[str, Any], class_def)
        for list_key in (
            "required_sections",
            "optional_sections",
            "forbidden_sections",
        ):
            for section in class_def_typed.get(list_key, []):
                if isinstance(section, str) and section not in sections:
                    errors.append(
                        f"class.{class_name}.{list_key}: unknown section '{section}'"
                    )

    for section_name, section_def in sections.items():
        if not isinstance(section_def, dict):
            continue

        section_def_typed = cast(dict[str, Any], section_def)
        section_field_defs = cast(dict[str, Any], fields.get(section_name, {}))

        for field_name in section_def_typed.get("allowed_fields", []):
            if isinstance(field_name, str) and field_name not in section_field_defs:
                errors.append(
                    f"section.{section_name}.allowed_fields: "
                    f"no field definition for '{section_name}.{field_name}'"
                )

    for section_name, section_field_defs_raw in fields.items():
        if not isinstance(section_field_defs_raw, dict):
            continue

        section_field_defs = cast(dict[str, Any], section_field_defs_raw)
        for field_name, field_def in section_field_defs.items():
            if not isinstance(field_def, dict):
                continue

            field_def_typed = cast(dict[str, Any], field_def)
            field_type = field_def_typed.get("type")

            if not isinstance(field_type, str) or field_type not in ALLOWED_FIELD_TYPES:
                errors.append(
                    f"field.{section_name}.{field_name}.type: "
                    f"unknown type '{field_type}'"
                )

    _validate_manifest_filename_schema(
        manifest=manifest,
        validation=validation,
        errors=errors,
    )
    _validate_contract_roles_schema(
        fields=fields,
        contract_roles=contract_roles,
        errors=errors,
    )

    return errors


def _validate_manifest_filename_schema(
    *,
    manifest: dict[str, Any],
    validation: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate manifest filename declaration consistency."""
    filename = manifest.get("filename")
    allowed_filenames = manifest.get("allowed_filenames")

    if validation.get("require_manifest_filename_exact") is True:
        errors.append(
            "validation.require_manifest_filename_exact: retired rule must not be "
            "enabled; use require_manifest_filename_allowed instead"
        )

    if validation.get("require_manifest_filename_allowed") is not True:
        errors.append(
            "validation.require_manifest_filename_allowed: must be true when "
            "manifest.allowed_filenames is authoritative"
        )
        return

    if not isinstance(filename, str) or not filename:
        errors.append("manifest.filename: must be a nonempty string")

    if not isinstance(allowed_filenames, list):
        errors.append("manifest.allowed_filenames: must be a list[string]")
        return

    invalid_items: list[Any] = [
        item
        for item in cast(list[Any], allowed_filenames)
        if not isinstance(item, str) or not item
    ]
    if invalid_items:
        errors.append("manifest.allowed_filenames: all values must be nonempty strings")

    if isinstance(filename, str) and filename not in allowed_filenames:
        errors.append(
            "manifest.allowed_filenames: must include canonical manifest.filename"
        )

    for required_name in REQUIRED_MANIFEST_FILENAMES:
        if required_name not in allowed_filenames:
            errors.append(
                f"manifest.allowed_filenames: missing required name '{required_name}'"
            )


def _validate_contract_roles_schema(
    *,
    fields: dict[str, Any],
    contract_roles: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate contract role registry consistency."""
    contract_fields = fields.get("contract", {})
    if not isinstance(contract_fields, dict):
        return

    contract_role_field = cast(dict[str, Any], contract_fields.get("contract_role", {}))  # type: ignore[arg-type]

    constraints = contract_role_field.get("constraints", [])
    if not isinstance(constraints, list):
        return

    if "known-contract-role" not in constraints:
        return

    allowed_raw = contract_roles.get("allowed")
    if not isinstance(allowed_raw, list):
        errors.append("contract_roles.allowed: required list missing")
        return

    invalid_roles = [
        role
        for role in cast(list[Any], allowed_raw)
        if not isinstance(role, str) or not role
    ]
    if invalid_roles:
        errors.append("contract_roles.allowed: all values must be nonempty strings")

    allowed_roles = {
        role for role in cast(list[Any], allowed_raw) if isinstance(role, str)
    }

    for role in sorted(REQUIRED_CONTRACT_ROLES - allowed_roles):
        errors.append(f"contract_roles.allowed: missing required role '{role}'")

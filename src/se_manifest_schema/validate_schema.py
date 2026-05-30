"""validate_schema.py - Validate manifest-schema.toml internal consistency."""

from typing import Any, cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData

REQUIRED_CONTRACT_ROLES = {"authority", "domain-contract"}
REQUIRED_MANIFEST_FILENAMES = ("SE_MANIFEST.toml", "MANIFEST.toml")

PRIMITIVE_FIELD_TYPES = {
    "string",
    "boolean",
    "integer",
}

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
    custom_types = _load_custom_types(schema)

    _validate_class_sections(
        classes=classes,
        sections=sections,
        errors=errors,
    )
    _validate_section_allowed_fields(
        sections=sections,
        fields=fields,
        errors=errors,
    )
    _validate_field_types(
        fields=fields,
        custom_types=custom_types,
        errors=errors,
    )
    _validate_custom_type_registry(
        schema=schema,
        custom_types=custom_types,
        errors=errors,
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


def _load_custom_types(schema: ManifestSchemaData) -> set[str]:
    """Load custom structured field types declared by the schema."""
    custom_types_raw = cast(dict[str, Any], schema.get("custom_types", {}))
    if not custom_types_raw:
        return set()

    allowed_raw = custom_types_raw.get("allowed", [])
    if not isinstance(allowed_raw, list):
        return set()

    return {
        item for item in cast(list[Any], allowed_raw) if isinstance(item, str) and item
    }


def is_known_type(type_name: str, custom_types: set[str]) -> bool:
    """Return whether a schema field type is known.

    Supports primitive types, custom structured types, and recursive list forms
    such as list[string] and list[dependency].
    """
    if type_name in PRIMITIVE_FIELD_TYPES:
        return True

    if type_name in custom_types:
        return True

    if type_name.startswith("list[") and type_name.endswith("]"):
        inner_type = type_name.removeprefix("list[").removesuffix("]")
        return is_known_type(inner_type, custom_types)

    if type_name.startswith("map[") and type_name.endswith("]"):
        inner_type = type_name.removeprefix("map[").removesuffix("]")
        return is_known_type(inner_type, custom_types)

    return False


def iter_field_definitions(
    field_tree: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    """Yield field definition tables that explicitly declare `type`."""
    results: list[tuple[str, dict[str, Any]]] = []

    def walk(prefix: list[str], node: object) -> None:
        if not isinstance(node, dict):
            return

        node_typed = cast(dict[str, Any], node)

        if "type" in node_typed:
            results.append((".".join(prefix), node_typed))

        for key, value in node_typed.items():
            walk([*prefix, key], value)

    walk([], field_tree)
    return results


def _validate_class_sections(
    *,
    classes: dict[str, Any],
    sections: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate that class section references point to known sections."""
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


def _validate_section_allowed_fields(
    *,
    sections: dict[str, Any],
    fields: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate that section allowed_fields have matching field definitions."""
    field_definitions = dict(iter_field_definitions(fields))

    for section_name, section_def in sections.items():
        if not isinstance(section_def, dict):
            continue

        section_def_typed = cast(dict[str, Any], section_def)

        for field_name in section_def_typed.get("allowed_fields", []):
            if not isinstance(field_name, str):
                continue

            field_path = f"{section_name}.{field_name}"
            if field_path not in field_definitions:
                errors.append(
                    f"section.{section_name}.allowed_fields: "
                    f"no field definition for '{field_path}'"
                )


def _validate_field_types(
    *,
    fields: dict[str, Any],
    custom_types: set[str],
    errors: list[str],
) -> None:
    """Validate all leaf field definition type declarations."""
    for field_path, field_def in iter_field_definitions(fields):
        field_type = field_def.get("type")

        if not isinstance(field_type, str) or not is_known_type(
            field_type,
            custom_types,
        ):
            errors.append(f"field.{field_path}.type: unknown type '{field_type}'")


def _validate_custom_type_registry(
    *,
    schema: ManifestSchemaData,
    custom_types: set[str],
    errors: list[str],
) -> None:
    """Validate custom structured type declarations."""
    custom_type_defs = cast(dict[str, Any], schema.get("custom_type", {}))

    for custom_type_name in sorted(custom_types):
        custom_type_def = custom_type_defs.get(custom_type_name)

        if not isinstance(custom_type_def, dict):
            errors.append(
                f"custom_types.allowed: missing custom_type.{custom_type_name}"
            )
            continue

        custom_type_def_typed = cast(dict[str, Any], custom_type_def)

        if custom_type_def_typed.get("kind") != "record":
            errors.append(f"custom_type.{custom_type_name}.kind: must be 'record'")

        fields_registry_name = custom_type_def_typed.get("fields")
        if not isinstance(fields_registry_name, str) or not fields_registry_name:
            errors.append(
                f"custom_type.{custom_type_name}.fields: must name a field registry"
            )
            continue

        registry = schema.get(fields_registry_name)
        if not isinstance(registry, dict):
            errors.append(
                f"custom_type.{custom_type_name}.fields: "
                f"unknown field registry '{fields_registry_name}'"
            )
            continue

        registry_typed = cast(dict[str, Any], registry)
        allowed_fields = cast(
            list[Any] | None, registry_typed.get("allowed_fields", None)
        )
        if not isinstance(allowed_fields, list) or not allowed_fields:
            errors.append(
                f"{fields_registry_name}.allowed_fields: required list missing"
            )


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
    contract_fields = cast(dict[str, Any], fields.get("contract", {}))

    contract_role_field = cast(dict[str, Any], contract_fields.get("contract_role", {}))

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

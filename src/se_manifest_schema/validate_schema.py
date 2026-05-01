"""validate_schema.py - Validates manifest-schema.toml internal consistency.

Checks:
  - all sections referenced in class definitions exist in section registry
  - all fields listed in section allowed_fields have field definitions
  - all field types are from the allowed set
"""

from typing import Any, cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData

ALLOWED_FIELD_TYPES = {"string", "boolean", "list[string]"}


def validate_schema_internal(schema: ManifestSchemaData) -> list[str]:
    """Validate internal consistency of manifest-schema.toml."""
    errors: list[str] = []

    sections_raw = schema.get("section", {})
    fields_raw = schema.get("field", {})
    classes_raw = schema.get("class", {})

    sections: dict[str, Any] = cast(dict[str, Any], sections_raw)
    fields: dict[str, Any] = cast(dict[str, Any], fields_raw)
    classes: dict[str, Any] = cast(dict[str, Any], classes_raw)

    # check all sections referenced in class definitions exist
    for class_name, class_def in classes.items():
        if not isinstance(class_def, dict):
            continue
        class_def_typed: dict[str, Any] = cast(dict[str, Any], class_def)
        for list_key in (
            "required_sections",
            "optional_sections",
            "forbidden_sections",
        ):
            for section in class_def_typed.get(list_key, []):
                if not isinstance(section, str):
                    continue
                if section not in sections:
                    errors.append(
                        f"class.{class_name}.{list_key}: unknown section '{section}'"
                    )

    # check all fields listed in section allowed_fields have field definitions
    for section_name, section_def in sections.items():
        if not isinstance(section_def, dict):
            continue
        section_def_typed: dict[str, Any] = cast(dict[str, Any], section_def)
        section_field_defs: dict[str, Any] = cast(
            dict[str, Any], fields.get(section_name, {})
        )
        for field_name in section_def_typed.get("allowed_fields", []):
            if not isinstance(field_name, str):
                continue
            if field_name not in section_field_defs:
                errors.append(
                    f"section.{section_name}.allowed_fields: "
                    f"no field definition for '{section_name}.{field_name}'"
                )

    # check all field types are from the allowed set
    for section_name, section_field_defs_raw in fields.items():
        if not isinstance(section_field_defs_raw, dict):
            continue
        section_field_defs_typed: dict[str, Any] = cast(
            dict[str, Any], section_field_defs_raw
        )
        for field_name, field_def in section_field_defs_typed.items():
            if not isinstance(field_def, dict):
                continue
            field_def_typed: dict[str, Any] = cast(dict[str, Any], field_def)
            field_type = field_def_typed.get("type")
            if not isinstance(field_type, str) or field_type not in ALLOWED_FIELD_TYPES:
                errors.append(
                    f"field.{section_name}.{field_name}.type: unknown type '{field_type}'"
                )

    return errors

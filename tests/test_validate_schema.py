"""test_validate_schema.py.

Tests for validate_schema.py and internal consistency of schema definitions.
"""

from typing import cast

from se_manifest_schema.types.manifest_schema import ManifestSchemaData
from se_manifest_schema.validate_schema import validate_schema_internal


def test_unknown_section_in_class_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"meta": {"allowed_fields": []}},
            "field": {},
            "class": {"fake": {"required_sections": ["meta", "nonexistent"]}},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonexistent" in error for error in errors)


def test_missing_field_definition_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repository": {"allowed_fields": ["name"]}},
            "field": {"repository": {}},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("repository.name" in error for error in errors)


def test_unknown_field_type_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repository": {"allowed_fields": ["name"]}},
            "field": {"repository": {"name": {"type": "badtype", "required": True}}},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("badtype" in error for error in errors)


def test_retired_exact_manifest_filename_rule_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {
                "require_manifest_filename_exact": True,
                "require_manifest_filename_allowed": True,
            },
        },
    )
    errors = validate_schema_internal(schema)
    assert any("require_manifest_filename_exact" in error for error in errors)


def test_missing_allowed_manifest_filename_rule_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("require_manifest_filename_allowed" in error for error in errors)


def test_manifest_filename_must_be_nonempty_string() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("manifest.filename" in error for error in errors)


def test_allowed_manifest_filenames_must_be_list() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": "SE_MANIFEST.toml",
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("manifest.allowed_filenames" in error for error in errors)


def test_allowed_manifest_filenames_must_include_canonical_filename() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("canonical manifest.filename" in error for error in errors)


def test_allowed_manifest_filenames_must_include_se_manifest() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "MANIFEST.toml",
                "allowed_filenames": ["MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("SE_MANIFEST.toml" in error for error in errors)


def test_allowed_manifest_filenames_must_include_manifest() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("MANIFEST.toml" in error for error in errors)


def test_contract_roles_registry_required_when_constraint_used() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("contract_roles.allowed" in error for error in errors)


def test_contract_roles_registry_must_include_authority() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "contract_roles": {"allowed": ["domain-contract"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("authority" in error for error in errors)


def test_contract_roles_registry_must_include_domain_contract() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "contract_roles": {"allowed": ["authority"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("domain-contract" in error for error in errors)


def test_allowed_manifest_filenames_with_empty_string_item_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml", ""],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonempty strings" in error for error in errors)


def test_contract_roles_with_empty_string_role_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {
                "contract": {
                    "contract_role": {
                        "type": "string",
                        "required": False,
                        "constraints": ["known-contract-role"],
                    }
                }
            },
            "class": {},
            "contract_roles": {"allowed": ["authority", "domain-contract", ""]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("nonempty strings" in error for error in errors)


def test_custom_type_missing_definition_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("custom_types.allowed" in error for error in errors)


def test_custom_type_kind_must_be_record() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "enum",  # wrong kind
                    "fields": "dependency_fields",
                }
            },
            "dependency_fields": {"allowed_fields": ["repository", "version"]},
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("kind" in error for error in errors)


def test_custom_type_fields_registry_missing_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    "fields": "nonexistent_registry",
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("unknown field registry" in error for error in errors)


def test_custom_type_fields_missing_allowed_fields_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    "fields": "dependency_fields",
                }
            },
            "dependency_fields": {},  # missing allowed_fields
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("allowed_fields" in error for error in errors)


def test_custom_type_with_missing_fields_key_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {},
            "field": {},
            "class": {},
            "custom_types": {"allowed": ["dependency"]},
            "custom_type": {
                "dependency": {
                    "kind": "record",
                    # "fields" key missing entirely
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("fields" in error for error in errors)


def test_is_known_type_list_primitive() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("list[string]", set())
    assert is_known_type("list[integer]", set())
    assert is_known_type("list[boolean]", set())


def test_is_known_type_map_primitive() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("map[string]", set())


def test_is_known_type_custom() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("dependency", {"dependency"})
    assert not is_known_type("unknown", set())


def test_is_known_type_list_custom() -> None:
    from se_manifest_schema.validate_schema import is_known_type

    assert is_known_type("list[dependency]", {"dependency"})


def test_iter_field_definitions_collects_typed_nodes() -> None:
    from se_manifest_schema.validate_schema import iter_field_definitions

    fields = {
        "repository": {
            "name": {"type": "string", "required": True},
            "class": {"type": "string", "required": True},
        }
    }
    results = iter_field_definitions(fields)
    paths = {path for path, _ in results}
    assert "repository.name" in paths
    assert "repository.class" in paths


def test_class_with_optional_and_forbidden_sections_unknown_detected() -> None:
    schema = cast(
        ManifestSchemaData,
        {
            "section": {"repository": {"allowed_fields": []}},
            "field": {},
            "class": {
                "myclass": {
                    "optional_sections": ["unknown-opt"],
                    "forbidden_sections": ["unknown-forb"],
                }
            },
            "manifest": {
                "filename": "SE_MANIFEST.toml",
                "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
            },
            "validation": {"require_manifest_filename_allowed": True},
        },
    )
    errors = validate_schema_internal(schema)
    assert any("unknown-opt" in error for error in errors)
    assert any("unknown-forb" in error for error in errors)


def _valid_minimal_schema_data() -> dict[str, object]:
    """Return a minimal internally consistent schema fixture."""
    return {
        "section": {
            "meta": {"allowed_fields": ["purpose"], "required": True},
            "repository": {
                "allowed_fields": ["name", "organization", "class"],
                "required": True,
            },
            "layer": {"allowed_fields": ["role"], "required": True},
            "depends": {"allowed_fields": ["required", "optional"], "required": True},
            "provides": {"allowed_fields": ["artifacts"], "required": True},
            "scope": {"allowed_fields": ["includes", "excludes"], "required": True},
            "compatibility": {
                "allowed_fields": ["constitution", "kernel", "schema"],
                "required": False,
            },
            "citation": {"allowed_fields": ["cff", "preferred"], "required": True},
            "traceability": {"allowed_fields": ["identifier_map"], "required": True},
        },
        "field": {
            "meta": {
                "purpose": {"required": False, "type": "string"},
            },
            "repository": {
                "name": {"required": True, "type": "string"},
                "organization": {"required": True, "type": "string"},
                "class": {"required": True, "type": "string"},
            },
            "layer": {
                "role": {"required": True, "type": "string"},
            },
            "depends": {
                "required": {"required": True, "type": "list[dependency]"},
                "optional": {"required": True, "type": "list[dependency]"},
            },
            "provides": {
                "artifacts": {"required": True, "type": "list[string]"},
            },
            "scope": {
                "includes": {"required": True, "type": "list[string]"},
                "excludes": {"required": True, "type": "list[string]"},
            },
            "compatibility": {
                "constitution": {"required": False, "type": "string"},
                "kernel": {"required": False, "type": "string"},
                "schema": {"required": False, "type": "list[string]"},
            },
            "citation": {
                "cff": {"required": True, "type": "string"},
                "preferred": {"required": True, "type": "string"},
            },
            "traceability": {
                "identifier_map": {"required": True, "type": "string"},
            },
            "dependency": {
                "repository": {"required": True, "type": "string"},
                "kind": {"required": True, "type": "string"},
            },
            "contract": {
                "contract_role": {
                    "required": False,
                    "type": "string",
                    "constraints": ["known-contract-role"],
                },
            },
        },
        "custom_types": {"allowed": ["dependency"]},
        "custom_type": {
            "dependency": {
                "kind": "record",
                "fields": "dependency_fields",
            },
        },
        "dependency_fields": {
            "allowed_fields": ["repository", "kind"],
        },
        "contract_roles": {"allowed": ["authority", "domain-contract"]},
        "manifest": {
            "filename": "SE_MANIFEST.toml",
            "allowed_filenames": ["SE_MANIFEST.toml", "MANIFEST.toml"],
        },
        "validation": {
            "require_manifest_filename_allowed": True,
            "require_class_required_sections_present": True,
            "require_sections_to_be_required_or_optional_for_class": True,
            "require_class_forbidden_sections_absent": True,
            "require_layer_role_to_match_declared_class": True,
            "require_compatibility_fields_for_class": True,
        },
        "class": {
            "specification": {
                "required_repo_name_patterns": ["accountable-{focus}-spec"],
                "required_layer_roles": ["specification"],
                "required_sections": [
                    "meta",
                    "repository",
                    "layer",
                    "depends",
                    "provides",
                    "scope",
                    "citation",
                    "traceability",
                ],
                "optional_sections": ["compatibility"],
                "forbidden_sections": [],
                "required_compatibility_fields": [],
            },
        },
    }


def _validation_table(data: dict[str, object]) -> dict[str, object]:
    """Return the validation table from a mutable schema fixture."""
    validation = data["validation"]
    assert isinstance(validation, dict)
    return cast(dict[str, object], validation)


def _specification_class_table(data: dict[str, object]) -> dict[str, object]:
    """Return the specification class table from a mutable schema fixture."""
    classes_raw = data["class"]
    assert isinstance(classes_raw, dict)
    classes = cast(dict[str, object], classes_raw)
    specification_raw = classes["specification"]
    assert isinstance(specification_raw, dict)
    return cast(dict[str, object], specification_raw)


def test_rejects_missing_class_validation_rule() -> None:
    """Schema validation requires class-registry enforcement rules."""
    data = _valid_minimal_schema_data()
    validation = _validation_table(data)
    validation.pop("require_class_required_sections_present")
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert "validation.require_class_required_sections_present: must be true" in errors


def test_rejects_class_without_required_layer_roles() -> None:
    """Every class must declare at least one allowed layer role."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["required_layer_roles"] = []
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert "class.specification.required_layer_roles: must not be empty" in errors


def test_rejects_class_without_required_repo_name_patterns() -> None:
    """Every class must declare at least one repository name pattern."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["required_repo_name_patterns"] = []
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert (
        "class.specification.required_repo_name_patterns: must not be empty" in errors
    )


def test_rejects_class_without_required_sections() -> None:
    """Every class must declare at least one required section."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["required_sections"] = []
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert "class.specification.required_sections: must not be empty" in errors


def test_rejects_required_optional_section_overlap() -> None:
    """A section cannot be both required and optional for one class."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["optional_sections"] = ["meta"]
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert (
        "class.specification: section 'meta' cannot be both required and optional"
        in errors
    )


def test_rejects_required_forbidden_section_overlap() -> None:
    """A section cannot be both required and forbidden for one class."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["forbidden_sections"] = ["repository"]
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert (
        "class.specification: section 'repository' cannot be both required and forbidden"
        in errors
    )


def test_rejects_optional_forbidden_section_overlap() -> None:
    """A section cannot be both optional and forbidden for one class."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["optional_sections"] = ["compatibility"]
    specification["forbidden_sections"] = ["compatibility"]
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert (
        "class.specification: section 'compatibility' cannot be both optional and forbidden"
        in errors
    )


def test_rejects_unknown_required_compatibility_field() -> None:
    """Required compatibility fields must be allowed compatibility fields."""
    data = _valid_minimal_schema_data()
    specification = _specification_class_table(data)
    specification["required_compatibility_fields"] = ["unknown_field"]
    errors = validate_schema_internal(cast(ManifestSchemaData, data))
    assert (
        "class.specification.required_compatibility_fields: "
        "unknown compatibility field 'unknown_field'"
    ) in errors

"""types/manifest_schema.py - Manifest schema artifact structure.

Represents manifest-schema.toml as loaded from TOML.
Uses functional TypedDict syntax because "class" is a real TOML key.
"""

from typing import TypedDict

from se_manifest_schema.types.primitives import ArtifactMeta

__all__ = [
    "ManifestSectionEntry",
    "ManifestFieldEntry",
    "ManifestClassEntry",
    "ManifestTable",
    "ContractRolesTable",
    "ValidationDefaultsTable",
    "ContractValidationTable",
    "ValidationTable",
    "ManifestSchemaData",
]


class ManifestSectionEntry(TypedDict, total=False):
    """Manifest section definition."""

    required: bool
    description: str
    allowed_fields: list[str]


class ManifestFieldEntry(TypedDict, total=False):
    """Manifest field definition."""

    type: str
    required: bool
    constraints: list[str]


class ManifestClassEntry(TypedDict, total=False):
    """Class-specific manifest requirements."""

    required_repo_name_patterns: list[str]
    required_layer_roles: list[str]
    required_sections: list[str]
    optional_sections: list[str]
    forbidden_sections: list[str]
    required_compatibility_fields: list[str]


class ManifestTable(TypedDict, total=False):
    """Manifest file contract."""

    filename: str
    allowed_filenames: list[str]
    human_legible: bool
    machine_readable: bool
    reviewable: bool
    identity: dict[str, object]


class ContractRolesTable(TypedDict, total=False):
    """Allowed contract role registry."""

    allowed: list[str]


class ValidationDefaultsTable(TypedDict, total=False):
    """Default validation behavior."""

    empty_optional_lists_allowed: bool
    empty_required_lists_allowed: bool


class ContractValidationTable(TypedDict, total=False):
    """Contract-specific validation rules."""

    contract_role_required_for_contract_class: bool
    contract_authority_required_for_contract_class: bool
    contract_version_required_for_contract_class: bool
    contract_role_must_be_known: bool
    contract_authority_must_equal_self: bool
    authority_role_must_not_consume_contract: bool
    domain_contract_role_must_consume_contract: bool
    domain_contract_must_not_consume_self: bool


class ValidationTable(TypedDict, total=False):
    """Validation rule table."""

    require_declared_class_to_exist_in_class_registry: bool
    require_dependencies_to_follow_dependency_law: bool
    require_dependency_kind: bool
    require_dependency_kind_to_be_known: bool
    require_known_fields_only: bool
    require_known_sections_only: bool
    require_manifest_filename_allowed: bool
    require_repository_name_to_match_declared_class: bool
    require_single_repository_class: bool
    require_class_required_sections_present: bool
    require_sections_to_be_required_or_optional_for_class: bool
    require_class_forbidden_sections_absent: bool
    require_layer_role_to_match_declared_class: bool
    require_compatibility_fields_for_class: bool

    defaults: ValidationDefaultsTable
    contract: ContractValidationTable


ManifestSchemaData = TypedDict(
    "ManifestSchemaData",
    {
        "meta": ArtifactMeta,
        "manifest": ManifestTable,
        "section": dict[str, ManifestSectionEntry],
        "field": dict[str, dict[str, ManifestFieldEntry]],
        "class": dict[str, ManifestClassEntry],
        "contract_roles": ContractRolesTable,
        "validation": ValidationTable,
    },
    total=False,
)

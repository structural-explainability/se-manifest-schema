"""validate_role_capability_map.py - Validate role-capability-map.toml."""

from collections.abc import Sequence
from pathlib import Path
import tomllib
from typing import Any, cast

__all__ = ["validate_role_capability_map_file", "validate_role_capability_map_data"]

REQUIRED_ROLE_CAPABILITY_MAP_SECTIONS = {
    "schema",
    "export",
    "consumers",
    "role_groups",
    "capability_profiles",
    "graph_permissions",
    "layer_order",
    "surface_buckets",
}

REQUIRED_SCHEMA_FIELDS = {
    "schema_id",
    "version",
    "status",
    "title",
    "description",
}

REQUIRED_EXPORT_FIELDS = {
    "path",
    "schema_path",
}

REQUIRED_CONSUMER_FIELDS = {
    "graph_verifier",
    "stage_verifier",
    "future_rust_verifier",
}

REQUIRED_CAPABILITY_FIELDS = {
    "validates_target_materials",
    "validates_resolution",
    "requires_lock_artifact",
    "exports_contract_artifacts",
    "emits_human_reports",
}

REQUIRED_GRAPH_PERMISSION_FIELDS = {
    "semantic_edge_kinds",
    "resolution_checked_edge_kinds",
    "entry_point_role_groups",
}

REQUIRED_GRAPH_RULES = {
    "no_core_depends_on_domain",
    "no_interpretation_leak",
    "no_contract_depends_on_implementation",
    "no_theory_bypass",
    "layer_monotonicity",
}

REQUIRED_SURFACE_BUCKETS = [
    "types",
    "predicates",
    "axioms",
    "theorems",
    "witnesses",
]

REQUIRED_SURFACE_CONSTANTS = [
    "SURFACE_TYPES",
    "SURFACE_PREDICATES",
    "SURFACE_AXIOMS",
    "SURFACE_THEOREMS",
    "SURFACE_WITNESSES",
]


def validate_role_capability_map_file(path: Path) -> list[str]:
    """Validate a role-capability-map.toml file."""
    if not path.exists():
        return [f"{path}: file does not exist"]

    with path.open("rb") as file:
        data = tomllib.load(file)

    return validate_role_capability_map_data(data)


def validate_role_capability_map_data(data: dict[str, Any]) -> list[str]:
    """Validate role-capability-map.toml internal consistency."""
    errors: list[str] = []

    _validate_required_top_level_sections(data=data, errors=errors)
    _validate_required_fields(
        table=cast(dict[str, Any], data.get("schema", {})),
        table_name="schema",
        required_fields=REQUIRED_SCHEMA_FIELDS,
        errors=errors,
    )
    _validate_required_fields(
        table=cast(dict[str, Any], data.get("export", {})),
        table_name="export",
        required_fields=REQUIRED_EXPORT_FIELDS,
        errors=errors,
    )
    _validate_required_fields(
        table=cast(dict[str, Any], data.get("consumers", {})),
        table_name="consumers",
        required_fields=REQUIRED_CONSUMER_FIELDS,
        errors=errors,
    )

    role_groups = cast(dict[str, Any], data.get("role_groups", {}))
    capability_profiles = cast(dict[str, Any], data.get("capability_profiles", {}))
    graph_permissions = cast(dict[str, Any], data.get("graph_permissions", {}))
    layer_order = cast(dict[str, Any], data.get("layer_order", {}))
    surface_buckets = cast(dict[str, Any], data.get("surface_buckets", {}))

    _validate_role_groups(role_groups=role_groups, errors=errors)
    _validate_capability_profiles(
        role_groups=role_groups,
        capability_profiles=capability_profiles,
        errors=errors,
    )
    _validate_graph_permissions(
        graph_permissions=graph_permissions,
        errors=errors,
    )
    _validate_layer_order(
        role_groups=role_groups,
        layer_order=layer_order,
        errors=errors,
    )
    _validate_surface_buckets(
        surface_buckets=surface_buckets,
        errors=errors,
    )

    return errors


def _validate_required_top_level_sections(
    *,
    data: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate required top-level sections."""
    for section in sorted(REQUIRED_ROLE_CAPABILITY_MAP_SECTIONS):
        if section not in data:
            errors.append(f"{section}: missing required section")
        elif not isinstance(data[section], dict):
            errors.append(f"{section}: section must be a table")


def _validate_required_fields(
    *,
    table: dict[str, Any],
    table_name: str,
    required_fields: set[str],
    errors: list[str],
) -> None:
    """Validate required fields in a table."""
    for field in sorted(required_fields):
        value = table.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{table_name}.{field}: must be a nonempty string")


def _validate_role_groups(
    *,
    role_groups: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate class-to-role-group bindings."""
    if not role_groups:
        errors.append("role_groups: must not be empty")
        return

    for repo_class, role_group in role_groups.items():
        if not repo_class:
            errors.append("role_groups: class names must be nonempty strings")

        if not isinstance(role_group, str) or not role_group:
            errors.append(f"role_groups.{repo_class}: must be a nonempty string")


def _validate_capability_profiles(
    *,
    role_groups: dict[str, Any],
    capability_profiles: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate role-group capability profiles."""
    declared_role_groups = _role_group_values(role_groups)

    for role_group in sorted(declared_role_groups):
        profile = capability_profiles.get(role_group)
        if not isinstance(profile, dict):
            errors.append(f"capability_profiles.{role_group}: missing profile")
            continue

        profile_typed = cast(dict[str, Any], profile)

        for field in sorted(REQUIRED_CAPABILITY_FIELDS):
            value = profile_typed.get(field)
            if not isinstance(value, bool):
                errors.append(
                    f"capability_profiles.{role_group}.{field}: must be boolean"
                )


def _validate_graph_permissions(
    *,
    graph_permissions: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate graph permission tables."""
    for field in sorted(REQUIRED_GRAPH_PERMISSION_FIELDS):
        value = graph_permissions.get(field)
        if not _is_list_of_nonempty_strings(value):
            errors.append(f"graph_permissions.{field}: must be list[string]")

    for rule_name in sorted(REQUIRED_GRAPH_RULES):
        rule = graph_permissions.get(rule_name)
        if not isinstance(rule, dict):
            errors.append(f"graph_permissions.{rule_name}: missing rule table")
            continue

        rule_typed = cast(dict[str, Any], rule)
        diagnostic = rule_typed.get("diagnostic")

        if not isinstance(diagnostic, str) or not diagnostic.startswith("SE.ORG."):
            errors.append(
                f"graph_permissions.{rule_name}.diagnostic: "
                "must be an SE.ORG diagnostic code"
            )

    _validate_forbidden_edge_rule(
        graph_permissions=graph_permissions,
        rule_name="no_core_depends_on_domain",
        errors=errors,
    )
    _validate_forbidden_edge_rule(
        graph_permissions=graph_permissions,
        rule_name="no_interpretation_leak",
        errors=errors,
    )
    _validate_forbidden_edge_rule(
        graph_permissions=graph_permissions,
        rule_name="no_contract_depends_on_implementation",
        errors=errors,
    )
    _validate_theory_bypass_rule(
        graph_permissions=graph_permissions,
        errors=errors,
    )
    _validate_layer_monotonicity_rule(
        graph_permissions=graph_permissions,
        errors=errors,
    )


def _validate_forbidden_edge_rule(
    *,
    graph_permissions: dict[str, Any],
    rule_name: str,
    errors: list[str],
) -> None:
    """Validate a source-role to forbidden-target-role rule."""
    rule = graph_permissions.get(rule_name)
    if not isinstance(rule, dict):
        return

    rule_typed = cast(dict[str, Any], rule)

    for field in ("source_role_groups", "forbidden_target_role_groups"):
        if not _is_list_of_nonempty_strings(rule_typed.get(field)):
            errors.append(
                f"graph_permissions.{rule_name}.{field}: must be list[string]"
            )


def _validate_theory_bypass_rule(
    *,
    graph_permissions: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate the no-theory-bypass rule table."""
    rule = graph_permissions.get("no_theory_bypass")
    if not isinstance(rule, dict):
        return

    rule_typed = cast(dict[str, Any], rule)

    for field in (
        "source_role_groups",
        "forbidden_target_role_groups",
        "allowed_intermediate_role_groups",
    ):
        if not _is_list_of_nonempty_strings(rule_typed.get(field)):
            errors.append(
                f"graph_permissions.no_theory_bypass.{field}: must be list[string]"
            )


def _validate_layer_monotonicity_rule(
    *,
    graph_permissions: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate the layer-monotonicity rule table."""
    rule = graph_permissions.get("layer_monotonicity")
    if not isinstance(rule, dict):
        return

    rule_typed = cast(dict[str, Any], rule)
    uses_layer_order = rule_typed.get("uses_layer_order")

    if uses_layer_order is not True:
        errors.append(
            "graph_permissions.layer_monotonicity.uses_layer_order: must be true"
        )


def _validate_layer_order(
    *,
    role_groups: dict[str, Any],
    layer_order: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate layer order entries for every declared role group."""
    declared_role_groups = _role_group_values(role_groups)

    for role_group in sorted(declared_role_groups):
        value = layer_order.get(role_group)
        if not isinstance(value, int):
            errors.append(f"layer_order.{role_group}: must be integer")


def _validate_surface_buckets(
    *,
    surface_buckets: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate theory surface bucket contract."""
    required = surface_buckets.get("required")
    constant_names = surface_buckets.get("constant_names")

    if required != REQUIRED_SURFACE_BUCKETS:
        errors.append(
            f"surface_buckets.required: must equal {REQUIRED_SURFACE_BUCKETS!r}"
        )

    if constant_names != REQUIRED_SURFACE_CONSTANTS:
        errors.append(
            f"surface_buckets.constant_names: must equal {REQUIRED_SURFACE_CONSTANTS!r}"
        )


def _role_group_values(role_groups: dict[str, Any]) -> set[str]:
    """Return declared role group values."""
    return {value for value in role_groups.values() if isinstance(value, str) and value}


def _is_list_of_nonempty_strings(value: object) -> bool:
    """Return whether value is a list of nonempty strings."""
    if not isinstance(value, list):
        return False

    items: Sequence[object] = cast(Sequence[object], value)
    return all(_is_nonempty_string(item) for item in items)


def _is_nonempty_string(value: object) -> bool:
    """Return whether value is a nonempty string."""
    return isinstance(value, str) and bool(value)

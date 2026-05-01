# Contribution Workflow

This document defines how changes are made to `se-manifest-schema`.

## Principles

- This repo owns only `manifest-schema.toml`
- Changes here affect all downstream repos that declare `SE_MANIFEST.toml`
- Validate before committing
- Tag every release — downstream repos pin by tag

## Standard workflow

### 1. Edit `manifest-schema.toml`

Changes may include:

- adding or modifying section definitions
- adding or modifying field definitions
- adding or modifying class requirements
- updating validation rules

### 2. Validate

```shell
uv run python -m se_manifest_schema validate
uv run pytest
```

### 3. Commit and tag

```shell
git add -A
git commit -m "Description of change"
git tag vX.Y.Z -m "X.Y.Z"
git push origin main
git push origin vX.Y.Z
```

## Common tasks

### Add a new section

1. Add `[section.name]` with `allowed_fields` list
2. Add `[field.name.field_name]` for every field in `allowed_fields`
3. Add section to relevant `[class.*]` `optional_sections` or `required_sections`
4. Validate

### Add a new field to an existing section

1. Add field name to `[section.name]` `allowed_fields`
2. Add `[field.section_name.field_name]` definition with `type` and `required`
3. Validate

### Add a new repository class

1. Add `[class.name]` with all required fields
2. Validate

### Fix validation failure

Always read the error message literally.

Typical causes:

- section referenced in class definition not declared in `[section.*]`
- field listed in `allowed_fields` has no `[field.section.name]` definition
- field type not in allowed set (`string`, `boolean`, `list[string]`)
- class used in `SE_MANIFEST.toml` not declared in `[class.*]`

## Design constraint

This repo defines structure only.
It does not validate downstream `SE_MANIFEST.toml` files directly.
Downstream repos import `validate_manifest` and run it themselves.

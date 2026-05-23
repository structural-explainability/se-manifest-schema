# Contribution Workflow

This document defines how changes are made to `se-manifest-schema`.

## Principles

- This repo owns `manifest-schema.toml`.
- Changes here affect downstream repositories that validate against this schema.
- Validate before committing.
- Tag every release.

## Standard workflow

### 1. Edit `manifest-schema.toml`

Changes may include:

- adding or modifying section definitions
- adding or modifying field definitions
- adding or modifying repository class requirements
- updating validation rules

### 2. Validate

```shell
uv run se-manifest validate-schema
uv run se-manifest validate-manifest --strict
uv run se-manifest check-version
uv run python -m pytest
```

### 3. Commit and release

See `CHANGELOG.md` for the release workflow.

## Common tasks

### Add a new section

1. Add `[section.name]` with an `allowed_fields` list.
2. Add field definitions for every field in `allowed_fields`.
3. Add the section to relevant class `required_sections` or `optional_sections`.
4. Validate.

### Add a new field to an existing section

1. Add the field name to the section's `allowed_fields`.
2. Add the field definition with `type` and `required`.
3. Validate.

### Add a new repository class

1. Add a `[class.name]` entry.
2. Define name patterns, layer roles, required sections, optional sections,
   forbidden sections, and required compatibility fields.
3. Validate.

### Fix validation failure

Read the error message literally.

Typical causes:

- a section is referenced by a class but not declared in `[section.*]`
- a field is listed in `allowed_fields` but has no field definition
- a field type is not in the allowed set
- a repository class is used but not declared in `[class.*]`

## Design constraint

This repo defines manifest structure and manifest validation rules.

It does not own downstream repository content, downstream release procedure,
or domain-specific contract data.

# Glossary

Definitions for terms used in `se-manifest-schema`.

## Manifest Schema

The file `manifest-schema.toml` at the repository root.
Defines what sections, fields, and class requirements are valid in any `SE_MANIFEST.toml`.

## SE_MANIFEST.toml

A repository declaration file conforming to the manifest schema.
Every SE ecosystem repository must have one.

## Section

A top-level TOML table in `SE_MANIFEST.toml` (e.g., `[repo]`, `[layer]`, `[scope]`).
Sections are defined in `[section.*]` entries in the schema.

## Field

A key-value pair within a section.
Fields are defined in `[field.section_name.field_name]` entries in the schema.

## Class

A named repository type declared in `[repo].class`.
Class-specific requirements are defined in `[class.*]` entries in the schema.

## Required Section

A section that must be present for a given class.
Declared in `[class.name].required_sections`.

## Optional Section

A section that may be present for a given class.
Declared in `[class.name].optional_sections`.

## Forbidden Section

A section that must not be present for a given class.
Declared in `[class.name].forbidden_sections`.

## Validation

The process of checking a `SE_MANIFEST.toml` against `manifest-schema.toml`.
Produces a list of errors. Empty list means valid.

## Breaking Change

A change to `manifest-schema.toml` that invalidates previously valid `SE_MANIFEST.toml` files.
Requires a major version bump.

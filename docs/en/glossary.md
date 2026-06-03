# Glossary

Definitions for terms used in `se-manifest-schema`.

## Manifest Schema

The file `manifest-schema.toml` at the repository root.
It defines valid sections, fields, repository classes, and validation rules for
SE-family repository manifests.

## Repository Manifest

A repository declaration file conforming to the manifest schema.
Supported filenames are:

- `SE_MANIFEST.toml`
- `MANIFEST.toml`

## Section

A top-level TOML table in a repository manifest.
Examples include `[repository]`, `[layer]`, and `[scope]`.
Sections are defined by `[section.*]` entries in the schema.

## Field

A key-value pair within a section.
Fields are defined by entries under `[field.*]` in the schema.

## Class

A repository type declared by `[repository].class`.
Class-specific requirements are defined by `[class.*]` entries in the schema.

## Required Section

A section that must be present for a given repository class.
Declared in a class entry's `required_sections`.

## Optional Section

A section that may be present for a given repository class.
Declared in a class entry's `optional_sections`.

## Forbidden Section

A section that must not be present for a given repository class.
Declared in a class entry's `forbidden_sections`.

## Validation

The process of checking a repository manifest against `manifest-schema.toml`.
A valid manifest produces no errors.

## Breaking Change

A change to `manifest-schema.toml` that invalidates previously valid repository
manifests.

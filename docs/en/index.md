# SE Manifest Schema

Defines the structure and validation rules for `SE_MANIFEST.toml`
across the Structural Explainability ecosystem.

## Contents

- [Contribution Workflow](./contribution-workflow.md)
- [Glossary](./glossary.md)
- [Manifest Schema](./manifest-schema.md)

## What this repo owns

One file: `manifest-schema.toml` at the repository root.

It defines what sections, fields, and class requirements
are valid in any `SE_MANIFEST.toml`.
Downstream repos import `validate_manifest` to check
their own manifests against this schema.

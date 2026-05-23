# SE Manifest Schema

Defines the structure and validation rules for SE repository manifests.

## Contents

- [Contribution Workflow](./contribution-workflow.md)
- [Glossary](./glossary.md)
- [Manifest Schema](./manifest-schema.md)

## What this repo owns

This repository owns the canonical manifest schema:

- `manifest-schema.toml`

The schema defines valid manifest sections, fields, repository classes,
and validation rules for SE-family repository manifests.

Supported manifest filenames are:

- `SE_MANIFEST.toml`
- `MANIFEST.toml`

Downstream repositories validate their own manifests against this schema by
using the `se-manifest` command-line interface.

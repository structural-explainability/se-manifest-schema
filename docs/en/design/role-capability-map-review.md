# Role Capability Map Review

The role capability map is a versioned control-plane contract artifact.
It binds manifest repository classes to role groups, role groups to
verifier capability profiles, and role groups to graph-permission rules.

This document records the review questions used to keep
`data/schema/role-capability-map.toml` durable.
It is intentionally descriptive rather than generated.
The generated checks should validate the map;
this document explains what the map is expected to mean.

## Review Status

Current status: draft

Release target: v1.0.0 control-plane consistency

Primary artifact:

```text
data/schema/role-capability-map.toml
```

Companion schema:

```text
data/schema/role-capability-map.schema.toml
```

Design specification:

```text
docs/en/design/manifest-graph-verification.md
```

## Review Principle

The map should encode durable authority boundaries.
The goal is to make drift inspectable, diagnosable, and testable.
The same class and role information is consumed by:

- manifest graph verification
- Accountable Record stage profile derivation
- future Rust conformance checks

## Review Dimensions

Each role group should be reviewed across four dimensions:

1. Role identity
2. Stage capability profile
3. Graph authority permissions
4. Release status

These dimensions are separate.
A repository can be active but not release-gate authoritative.
A repository can be consumed as tooling without becoming semantic authority.
A role group can emit reports without exporting contract artifacts.

## Role Group Review Table

Use this table to review each role group declared in
`data/schema/role-capability-map.toml`.

| Role group      | Manifest classes | Validates target materials | Validates resolution | Requires lock artifact | Exports contract artifacts | Emits human reports | Layer order reviewed | Status | Notes                                                                               |
| --------------- | ---------------- | -------------------------: | -------------------: | ---------------------: | -------------------------: | ------------------: | -------------------: | ------ | ----------------------------------------------------------------------------------- |
| adapter         | adapter          |                      false |                false |                  false |                      false |               false |                   no | draft  | Review whether adapters should emit reports.                                        |
| administration  | admin            |                      false |                false |                  false |                      false |                true |                   no | draft  | Administrative repos may coordinate checks without becoming semantic authority.     |
| constitution    | constitution     |                       true |                 true |                   true |                      false |                true |                   no | draft  | Review whether constitution exports contract artifacts or remains governance-only.  |
| contract        | contract         |                       true |                 true |                   true |                       true |                true |                   no | draft  | Contract repos are semantic contract surfaces.                                      |
| data            | data_companion   |                       true |                 true |                   true |                      false |                true |                   no | draft  | Review whether all data companion repos require locks.                              |
| documentation   | docs             |                      false |                false |                  false |                      false |                true |                   no | draft  | Documentation is curated output, not semantic authority.                            |
| formal_contract | formal_contract  |                       true |                 true |                   true |                       true |                true |                   no | draft  | Bridges formal theory to operational contract artifacts.                            |
| govsrc          | govsrc           |                       true |                 true |                   true |                      false |                true |                   no | draft  | Source registries can be terminal entry points.                                     |
| implementation  | implementation   |                       true |                 true |                   true |                      false |                true |                   no | draft  | Implementations verify or consume contracts; they do not define contract semantics. |
| kernel          | kernel           |                       true |                 true |                   true |                       true |                true |                   no | draft  | Review relation between kernel and constitution.                                    |
| manifest_schema | manifest_schema  |                       true |                 true |                   true |                       true |                true |                   no | draft  | Owns manifest structure and graph-validation semantics.                             |
| mapping         | mapping          |                       true |                 true |                   true |                      false |                true |                   no | draft  | Mapping should not leak interpretation into substrate or boundary layers.           |
| mapspec         | mapspec          |                       true |                 true |                   true |                       true |                true |                   no | draft  | Mapping specifications may export structured artifacts.                             |
| pilot           | pilot            |                      false |                false |                  false |                      false |                true |                   no | draft  | Pilots may remain incomplete without blocking v1.0.0.                               |
| policy          | policy           |                       true |                 true |                   true |                      false |                true |                   no | draft  | Review whether policy should export contract-like artifacts.                        |
| profile         | profile          |                       true |                 true |                   true |                      false |                true |                   no | draft  | Profiles constrain application contexts but should not override substrate.          |
| record_system   | record_system    |                       true |                 true |                   true |                      false |                true |                   no | draft  | Domain record systems should consume contracts, not define foundation semantics.    |
| regimes         | regimes          |                       true |                 true |                   true |                      false |                true |                   no | draft  | Review whether regimes should be folded into contract artifacts later.              |
| rules           | rules            |                       true |                 true |                   true |                      false |                true |                   no | draft  | Jurisdictional or context rules remain external to substrate.                       |
| schema          | schema           |                       true |                 true |                   true |                       true |                true |                   no | draft  | Domain or exchange schemas may export machine-readable artifacts.                   |
| specification   | specification    |                       true |                 true |                   true |                      false |                true |                   no | draft  | Specifications may be provenance, transitional, or canonical depending on manifest. |
| theory          | theory           |                       true |                 true |                   true |                      false |                true |                   no | draft  | Theory exports formalized knowledge, not operational machine-readable artifacts.    |
| tooling         | engine           |                      false |                false |                  false |                      false |                true |                   no | draft  | Tooling dependencies are real dependencies but not semantic authority edges.        |
| verification    | verification     |                       true |                 true |                   true |                      false |                true |                   no | draft  | Verification repos check records without defining contract authority.               |
| verifier        | verifier         |                       true |                 true |                   true |                      false |                true |                   no | draft  | Standalone verifiers consume contracts and emit reports.                            |

## Capability Questions

For each role group, answer these questions before marking it reviewed.

### validates_target_materials

Does this role group validate authored or declared target materials?

Examples of target materials include manifests, source declarations, element
declarations, catalog declarations, theory surfaces, mapping tables, schemas,
rules, source registries, and record inputs.

Use `true` only when the role group is expected to inspect domain or contract
materials as part of its own verification profile.

### validates_resolution

Does this role group validate references, dependency resolution, provenance
links, or lock state?

Use `true` when the role group participates in reference resolution or must prove
that its upstream references are coherent.

### requires_lock_artifact

Does this role group require a lock, digest, or provenance artifact even when the
artifact is empty-but-valid?

Use `true` when absence of external references should still be represented as an
empty-but-valid lock state rather than omitted.

### exports_contract_artifacts

Does this role group export machine-readable artifacts consumed downstream as
contract or schema authority?

Use `true` for contract, formal contract, schema, kernel, manifest schema, or
other roles that intentionally provide machine-readable authority surfaces.

Use `false` for roles that report, verify, document, or implement without
becoming contract authority.

### emits_human_reports

Does this role group emit human-readable reports as part of its expected
verification or governance surface?

Use `true` when a verifier, checker, or release gate should produce Markdown or
other human-readable review material.

## Graph-Permission Review

Graph permissions apply to semantic dependency edges only.
Tooling dependencies are still real dependencies.
They must resolve and they must name valid repositories.
They do not confer semantic authority.
Review each graph rule separately.

## SI01: Required semantic dependency graph is acyclic

Question:

```text
Can a required semantic dependency cycle exist without creating circular authority?
```

Expected answer: no

Review status: draft

## SI02: All declared dependencies resolve

Question:

```text
Does every declared dependency, regardless of kind, resolve to a real repository
with a valid manifest?
```

Expected answer: yes

Review status: draft

## SI03: Provides are real

Question:

```text
Does every declared provided artifact exist on disk or in a declared release?
```

Expected answer: yes

Review status: draft

## SI04: Class registry is satisfied

Question:

```text
Does each repository declare every section required by its manifest class?
```

Expected answer: yes

Review status: draft

## SG01: No core depends on domain

Question:

```text
Can a core, substrate, boundary, kernel, or manifest-schema role depend
semantically on domain, application, example, govsrc, or record-system roles?
```

Expected answer: no

Review status: draft

## SG02: Interpretation stays external

Question:

```text
Can substrate, boundary, or kernel roles depend semantically on mapping or
government-source roles?
```

Expected answer: no

Review status: draft

## SG03: Implementations are not semantic authority

Question:

```text
Can contract, formal-contract, schema, or record-system roles depend
semantically on implementation, verification, or verifier roles?
```

Expected answer: no

Review status: draft

## SG04: Operational systems do not consume theory directly

Question:

```text
Can operational implementations, record systems, applications, or verifiers
depend semantically on theory repos directly?
```

Expected answer: no. The semantic path should run through formal-contract or
other declared contract surfaces.

Review status: draft

## SG05: Layer monotonicity

Question:

```text
Does each semantic dependency point toward an equal or more foundational layer?
```

Expected answer: yes

Review status: draft

## CG01: No non-terminal orphans

Question:

```text
Is every active non-terminal role group consumed by at least one other repo,
unless it declares an accepted status or is an entry-point root?
```

Expected answer: yes

Review status: draft

## CG02: Formalization sources are classified

Question:

```text
Is each formalization result classified per artifact as canonical, auxiliary,
transitional, or superseded?
```

Expected answer: yes

Review status: draft

## Surface bucket review

Theory surface mirrors must expose these semantic-role buckets:

```text
SURFACE_TYPES
SURFACE_PREDICATES
SURFACE_AXIOMS
SURFACE_THEOREMS
SURFACE_WITNESSES
```

A bucket may be empty, but it must exist.

Review question:

```text
Does each theory repo classify public Lean symbols by semantic role rather than
Lean keyword category?
```

Expected answer: yes

Review status: draft

## Formalization status review

Formalization status belongs under the provided artifact, not at repo level.

Example:

```toml
[provides.formalization.identity_regime_lower_bound]
kind = "lean-theorem-set"
status = "canonical"
symbols = [
    "IdentityRegime.lowerBound",
]
```

Allowed statuses:

```text
canonical
auxiliary
transitional
superseded
```

Review question:

```text
Does each formalization artifact declare whether it is canonical, auxiliary,
transitional, or superseded?
```

Expected answer: yes

Review status: draft

## Dependency kind review

Each dependency should declare a kind.

First required kinds:

```text
semantic
tooling
```

Reserved kinds:

```text
documentation
test
release
provenance
```

Review question:

```text
Does each dependency distinguish semantic authority from tooling or other
support use?
```

Expected answer: yes

Review status: draft

## Release-Gate Checklist

Before v1.0.0, complete these checks:

- Every manifest class in `manifest-schema.toml` appears in `role_groups`.
- Every role group in `role_groups` has one capability profile.
- Every role group in `role_groups` has one layer-order value.
- Every graph rule has a stable `SE.ORG.*` diagnostic.
- Every required theory surface bucket is present in each theory mirror.
- Every semantic dependency kind is reviewed.
- Every tooling dependency kind is reviewed.
- Every canonical formalization source is declared per provided artifact.
- Every duplicate formalization source is classified.
- Every accepted orphan has a recorded reason.
- The AR verifier consumes `role_groups` and `capability_profiles`.
- The graph verifier consumes `role_groups` and `graph_permissions`.
- Future Rust conformance expectations reference this same artifact.

## Change policy

Changes to `data/schema/role-capability-map.toml` should be treated as
contract changes, not ordinary configuration edits.

Every change should answer:

```text
Which consumer is affected?
Which capability, graph rule, or role binding changes?
Is this a breaking change for any verifier?
Does the change require a fixture update?
Does the change require a diagnostic-code update?
```

## Open review items

- Confirm whether `adapter` should emit human reports.
- Confirm whether `constitution` should export contract artifacts.
- Confirm whether all `data` roles require lock artifacts.
- Confirm relation between `kernel` and `constitution`.
- Confirm whether `policy` should export contract-like artifacts.
- Confirm whether `regimes` should eventually feed formal-contract exports.
- Confirm layer order values after the first graph report is generated.
- Confirm the first canonical formalization declarations under
  `[provides.formalization.*]`.

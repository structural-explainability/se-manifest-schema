# Manifest Graph Verification

Manifest graph verification extends the Structural Explainability manifest layer from
single-repository validation to organization-level dependency validation.
It adds a graph pass to the existing `se-manifest` control plane.
It does not introduce a separate verifier product.
The graph pass checks whether the repository structure preserves
the same distinctions the framework requires of Accountable Records.

## Purpose

`SE_MANIFEST.toml` declares repository identity, class, layer role, dependencies, and provided artifacts.
`manifest-schema.toml` defines the allowed shape of those declarations.
`data/schema/role-capability-map.toml` binds manifest classes to role groups,
role groups to verifier capability profiles, and role groups to graph-permission rules.
Manifest graph verification answers this question:

```text
Does the repository graph preserve Structural Explainability boundaries?
```

The goal is to make cross-repository drift visible before release.
Missing manifests, unresolved dependencies, dependency cycles,
undeclared provided artifacts, interpretation leaks, direct theory bypasses,
and duplicate formalization paths should become diagnostics instead of manual discoveries.

## Non-Goals

Manifest graph verification makes selected structural drift inspectable, diagnosable, and testable.
It does not:

- replace `validate-manifest`
- replace repository-local tests
- replace Accountable Record stage validation
- prove that domain content is true
- prove that evidence is semantically adequate
- make drift impossible

## Inputs

The graph verifier reads these control-plane artifacts:

- repository manifests
- `manifest-schema.toml`
- `data/schema/role-capability-map.toml`
- declared provided artifacts
- optional formalization declarations

### Repository Manifest Inputs

Each repository is expected to declare identity, role, dependencies, and provided artifacts.

```toml
[repo]
name = "example-repo"
org = "structural-explainability"
class = "implementation"
kind = "python-package"
status = "active"
since = "2026"
summary = "Example repository."

[layer]
space = "implementation"
role = "verifier-implementation"

[depends]
required = [
    { repo = "accountable-record", kind = "semantic" },
]
optional = [
    { repo = "se-contract-kit", kind = "tooling" },
]

[provides]
artifacts = [
    "src/example",
]
```

A repository with no `SE_MANIFEST.toml` is not silently skipped.
It emits `SE.ORG.MISSING_MANIFEST`.

### Manifest Schema Inputs

The graph verifier reads `manifest-schema.toml` for:

- known sections
- known fields
- known repository classes
- class-specific required sections
- dependency declaration shape
- provided artifact declaration shape

### Role Capability Map Inputs

The graph verifier reads `data/schema/role-capability-map.toml`.
The role capability map provides:

- manifest class to role group bindings
- role group to graph-permission rules
- role group layer order
- semantic surface bucket requirements

The graph verifier consumes:

- `role_groups`
- `graph_permissions`
- `layer_order`
- `surface_buckets`

The Accountable Record stage verifier consumes:

- `role_groups`
- `capability_profiles`

Both tools read the same class-to-role binding.
Neither tool redefines it locally.

### Provided Artifact Inputs

The graph verifier checks declared provided artifacts against the
repository tree or declared release surface.
For formalization results, manifests may declare per-artifact formalization status.

```toml
[provides.formalization.identity_regime_lower_bound]
kind = "lean-theorem-set"
status = "canonical"
symbols = [
    "IdentityRegime.lowerBound",
]
```

Formalization status belongs to the provided artifact, not to the whole repository.
Allowed statuses are:

- `canonical`
- `auxiliary`
- `transitional`
- `superseded`

## Dependency Kinds

Each dependency edge has a kind.
Initial required kinds are:

- `semantic`
- `tooling`

Reserved kinds are:

- `documentation`
- `test`
- `release`
- `provenance`

All dependency edges must resolve.
Only semantic edges participate in authority rules.
Tooling dependencies are real dependencies for installation and CI.
Tooling dependencies do not confer semantic authority.
For example, a theory repository may depend on `se-contract-kit` to run surface drift checks.
That dependency should resolve, but it should not be interpreted
as the theory repository deriving semantic authority from `se-contract-kit`.

## Graph Model

The graph verifier builds a directed dependency graph.
Nodes are repositories.
Node attributes include:

- repository name
- repository class
- layer space
- layer role
- normalized role group
- repository status

Edges are declared dependencies.
Edge attributes include:

- source repository
- target repository
- required or optional
- dependency kind
- optional version or reason metadata

The required semantic dependency graph is the authority graph used for cycle and layer-direction checks.

## Diagnostic Namespace

Manifest graph diagnostics use the `SE.ORG.*` namespace.
This mirrors the staged Accountable Record diagnostic pattern
while keeping organization-level diagnostics separate from record-level diagnostics.
Examples:

```text
SE.ORG.MISSING_MANIFEST
SE.ORG.UNRESOLVED_DEPENDENCY
SE.ORG.DEPENDENCY_CYCLE
SE.ORG.MISSING_PROVIDED_ARTIFACT
SE.ORG.CORE_DEPENDS_ON_DOMAIN
SE.ORG.THEORY_BYPASS
```

Diagnostic codes are part of the public conformance surface.
They should be stable once released.

## Graph Invariants

Graph invariants are split into structural checks, semantic policy checks, and classification checks.
Structural checks are the first implementation slice.
Semantic policy checks are enabled after `role-capability-map.toml` is populated and reviewed.

### Structural Invariants (SI)

| Code | Name                                          | Rule                                                                                            | Diagnostic                         |
| ---- | --------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------- |
| SI01 | Required semantic dependency graph is acyclic | The required semantic dependency graph must be acyclic.                                         | `SE.ORG.DEPENDENCY_CYCLE`          |
| SI02 | All declared dependencies resolve             | Every declared dependency must resolve to a known repository with a valid manifest.             | `SE.ORG.UNRESOLVED_DEPENDENCY`     |
| SI03 | Provides are real                             | Every artifact declared under `[provides]` must exist on disk or in a declared release surface. | `SE.ORG.MISSING_PROVIDED_ARTIFACT` |
| SI04 | Class registry is satisfied                   | Each repository must declare every section required by its manifest class.                      | `SE.ORG.MISSING_REQUIRED_SECTION`  |

### Semantic Graph Invariants (SG)

| Code | Name                                               | Rule                                                                                                                      | Diagnostic                        |
| ---- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| SG01 | No domain semantics in the core                    | Foundational roles must not derive semantic authority from domain roles.                                                  | `SE.ORG.CORE_DEPENDS_ON_DOMAIN`   |
| SG02 | Interpretation stays external                      | Interpretive mappings and source registries remain outside substrate, boundary, and kernel roles.                         | `SE.ORG.INTERPRETATION_LEAK`      |
| SG03 | Implementations are not semantic authority         | Implementations consume or verify contracts; they do not define contract semantics.                                       | `SE.ORG.CONTRACT_DEPENDS_ON_IMPL` |
| SG04 | Operational systems do not consume theory directly | The semantic path from theory to operation passes through declared contract surfaces, especially formal-contract outputs. | `SE.ORG.THEORY_BYPASS`            |
| SG05 | Layer monotonicity                                 | A semantic edge must not point from a more foundational layer to a less foundational layer.                               | `SE.ORG.LAYER_INVERSION`          |

### Classification Graph Invariants (CG)

| Code | Name                                 | Rule                                                                                                                                                      | Diagnostic                       | Default severity            |
| ---- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | --------------------------- |
| CG01 | No non-terminal orphans              | Every active non-terminal role group should be consumed by at least one other repository unless it declares an accepted status or is an entry-point root. | `SE.ORG.ORPHAN`                  | warning                     |
| CG02 | Formalization sources are classified | Each formalization result feeding `se-formal-contract` should declare whether it is canonical, auxiliary, transitional, or superseded.                    | `SE.ORG.DUPLICATE_FORMALIZATION` | warning before release gate |

## Encoding Agreement Checks (E)

Encoding agreement checks compare two encodings of the same commitment.
The common pattern is:

```text
Representation A and Representation B describe one commitment.
If they disagree, report drift.
```

| Code | Name                     | Representation A                | Representation B                                  | Diagnostic                                        |
| ---- | ------------------------ | ------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| E1   | Surface mirror drift     | `Surface.lean` exported symbols | `lean_surface.py` `SURFACE_*` constants           | `SE.ORG.SURFACE_DRIFT`                            |
| E2   | Cell matrix drift        | Lean classification cells       | TOML classification cells                         | `SE.ORG.CELL_COUNT_MISMATCH`                      |
| E3   | Paper traceability drift | paper `cite_id` declarations    | Lean theorem, predicate, type, or witness symbols | `SE.ORG.UNTRACED_CLAIM`, `SE.ORG.UNCITED_THEOREM` |
| E4   | Reference coverage       | reference artifacts             | `SURFACE_SYMBOLS`                                 | existing reference validation                     |
| E5   | Manifest provides drift  | `[provides]` declarations       | files or release assets                           | `SE.ORG.MISSING_PROVIDED_ARTIFACT`                |

Theory surface mirrors must expose these semantic buckets:

```text
SURFACE_TYPES
SURFACE_PREDICATES
SURFACE_AXIOMS
SURFACE_THEOREMS
SURFACE_WITNESSES
```

A bucket may be empty, but it must exist.
The buckets are semantic roles, not Lean keyword categories.
A `def` may be a predicate, witness, classifier, helper, constructor, or executable adapter.
The author classifies public symbols by semantic role.

## Role Capability Map Invariants

The role capability map is a versioned contract artifact, not helper config.
Path:

```text
data/schema/role-capability-map.toml
```

Companion schema:

```text
data/schema/role-capability-map.schema.toml
```

The map is internally separated into consumer-specific slices.

```toml
[schema]
schema_id = "se-role-capability-map-1"
version = "0.1.0"

[role_groups]
# manifest class -> role group

[capability_profiles]
# role group -> verifier and stage capabilities

[graph_permissions]
# role group -> semantic edge rules
```

The Accountable Record verifier reads:

- `role_groups`
- `capability_profiles`

The graph verifier reads:

- `role_groups`
- `graph_permissions`
- `layer_order`
- `surface_buckets`

Both share the same class-to-role binding.

## Severity Policy

Structural and semantic graph violations fail the build.

Classification findings warn until release gate.

At release gate, warnings must either be resolved or explicitly accepted with a recorded reason.
This mirrors Accountable Record authority decision:
absence, emptiness, and opt-out are distinct states.
An accepted exception should be recorded.

## CLI Output

The command should emit both machine-readable and human-readable reports.
Recommended output paths:

```text
data/export/org-graph-report.json
data/reports/org-graph-report.md
```

The report should include:

- repository count
- missing manifest list
- dependency graph summary
- required semantic graph summary
- dependency kind counts
- per-invariant pass/fail results
- diagnostics with repository context
- orphan list
- duplicate formalization list
- provided-artifact findings
- surface and traceability findings when enabled

## CLI Command

The graph pass should be exposed as an explicit command first.

```text
se-manifest verify-graph
```

It should remain separate from `validate-manifest --strict` while the graph layer is new.
Later, strict validation may call both commands, or a release-gate command may run both.

```text
se-manifest validate-manifest --strict
se-manifest verify-graph --strict
```

## Placement And Ownership

| Piece                      | Location                                                           |
| -------------------------- | ------------------------------------------------------------------ |
| Spec                       | `se-manifest-schema/docs/en/design/manifest-graph-verification.md` |
| CLI command                | `se-manifest verify-graph`                                         |
| Package                    | `se-manifest-schema/src/se_manifest_schema/`                       |
| Graph code                 | `src/se_manifest_schema/graph/`                                    |
| Role capability map        | `data/schema/role-capability-map.toml`                             |
| Role capability map schema | `data/schema/role-capability-map.schema.toml`                      |
| Manifest schema support    | `manifest-schema.toml`                                             |
| Reusable E1-E3 checks      | `se-contract-kit/src/se_contract_kit/checks/`                      |
| Per-repo declarations      | `SE_MANIFEST.toml`, `Surface.lean`, `lean_surface.py`              |

Ownership order:

- `se-manifest-schema` owns manifest structure, class-to-role mapping,
- role-to-capability mapping, and manifest graph validation.
- `se-contract-kit` owns reusable cross-encoding checks over formal-contract and theory artifacts.
- Theory repositories own their Lean surfaces and per-symbol bucket judgments.
- Accountable Record implementations consume the shared role capability map; they do not redefine it.
- Future Rust conformance checks consume the same map.

## First Implementation Slice

The first slice should prove the mechanism before encoding every policy edge rule.
Scope:

- load all accessible repository manifests
- emit `SE.ORG.MISSING_MANIFEST` for absent manifests
- parse structured dependency entries
- distinguish required and optional dependencies
- distinguish semantic and tooling dependencies
- build the dependency graph
- validate SI01, SI02, SI03, and SI04
- emit JSON and Markdown reports

SI01, SI02, SI03, and SI04 do not require the full policy table.
They are graph and structure facts.
Policy rules SG01 through SG05 should be switched on after
`role-capability-map.toml` is populated and reviewed.

## Release Gate

Before v1.0.0, the graph verifier should confirm:

- all manifests are present or missing manifests are explicitly accepted
- all declared dependencies resolve
- the required semantic graph is acyclic
- semantic edge rules pass or have explicit accepted exceptions
- every class in `manifest-schema.toml` has a role group
- every role group has a capability profile
- every role group has a layer order
- every provided artifact exists
- formalization sources are classified
- theory surface buckets are present
- graph diagnostics are stable
- report outputs are generated

## Change Policy

Changes to manifest graph verification are contract-surface changes when they affect:

- dependency kind interpretation
- role group assignment
- capability profile derivation
- graph permission rules
- diagnostic codes
- release-gate severity
- required outputs

Each such change should answer:

- Which consumer is affected?
- Is the change backward-compatible?
- Does this require fixture updates?
- Does this require diagnostic-code changes?
- Does this affect Python/Rust conformance?

## Current Status

Status: draft.
The current implementation target is a first working graph slice.
The map and schema are draft control-plane artifacts until the
graph verifier consumes them and at least SI01, SI02, SI03, and SI04 are covered by tests.

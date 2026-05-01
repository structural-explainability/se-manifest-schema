"""types/primitives.py - Shared primitive type definitions."""

from typing import Any, TypedDict

# WHY: One parsed TOML document is the broad boundary type returned by loaders.
# WHY: Keep this reusable and artifact-agnostic.
TomlData = dict[str, Any]

# WHY: Artifact names are stable string keys used in collections of loaded data.
ArtifactName = str

# WHY: A repository-level loaded data set is a mapping of artifact name to TOML document.
# WHY: Keep this broad; narrower artifact-specific types belong in artifact-specific files.
ArtifactCollection = dict[ArtifactName, TomlData]


class ArtifactMeta(TypedDict, total=False):
    """Common metadata header present in all constitutional artifact files."""

    version: str
    status: str
    title: str

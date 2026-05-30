"""Diagnostics for manifest graph verification."""

from dataclasses import dataclass
from pathlib import Path

__all__ = ["GraphDiagnostic"]


@dataclass(frozen=True)
class GraphDiagnostic:
    """One manifest graph verification diagnostic."""

    code: str
    message: str
    repo: str | None = None
    path: str | None = None

    def render(self, root: str | Path | None = None) -> str:
        """Render the diagnostic across several short lines.

        The code is the first line; repo, path, and message each get their
        own indented line so no single line carries every field at once.

        Args:
            root: If given, the path is shown relative to it, keeping the
                path line readable instead of carrying a full absolute path.

        Returns:
            A multi-line string for the diagnostic.
        """
        lines = [self.code]

        if self.repo:
            lines.append(f"    repo  {self.repo}")

        if self.path:
            shown = self.path
            if root is not None:
                try:
                    shown = str(Path(self.path).relative_to(root))
                except ValueError:
                    shown = self.path
            lines.append(f"    path  {shown}")

        lines.append(f"    {self.message}")
        return "\n".join(lines)

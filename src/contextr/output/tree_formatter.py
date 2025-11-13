"""
Tree structure formatting functionality.
"""

from pathlib import Path
from typing import Any


def generate_tree_structure(files: list[Path], root: Path) -> str:
    """
    Generate a tree structure representation of the files.

    Args:
        files: List of file paths
        root: Root directory path

    Returns:
        String representation of the directory tree
    """
    tree: dict[str, Any] = {}

    for file_path in files:
        try:
            relative_path = file_path.relative_to(root)
            parts = relative_path.parts

            current: dict[str, Any] = tree
            for part in parts[:-1]:  # All except the file name
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add the file
            current[parts[-1]] = None

        except ValueError:
            continue

    # Convert tree to string representation
    return _format_tree(tree, "", True)


def _format_tree(tree: dict, prefix: str = "", is_last: bool = True) -> str:
    """Recursively format the tree structure."""
    lines = []
    items = sorted(
        tree.items(), key=lambda x: (x[1] is not None, x[0])
    )  # Dirs first, then files

    for i, (name, subtree) in enumerate(items):
        is_last_item = i == len(items) - 1

        if subtree is None:  # It's a file
            lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}")
        else:  # It's a directory
            lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}/")
            extension = "    " if is_last_item else "│   "
            lines.append(_format_tree(subtree, prefix + extension, is_last_item))

    return "\n".join(filter(None, lines))

"""
Token counting commands for repository analysis.
"""

import sys
from pathlib import Path

from ..discovery import discover_files
from ..formatters.token_tree_formatter import TokenTreeFormatter
from ..statistics import TokenCounter


def determine_repo_root(paths: list[Path]) -> Path:
    """
    Determine the repository root from the given paths.

    For single file, use its directory.
    For multiple files, find common parent.
    For directories, use the directory itself.
    """
    import os

    if len(paths) == 1:
        if paths[0].is_file():
            return paths[0].parent
        else:
            return paths[0]

    # Find common parent for multiple paths
    common_parent = Path(os.path.commonpath([str(p) for p in paths]))
    return common_parent


def token_count_tree_command(
    paths: list[str],
    include_pattern: str | None = None,
    show_tree: bool = True,
    tokens_only: bool = False,
    threshold: int = 0,
) -> str:
    """
    Generate token count visualization for the repository.

    Args:
        paths: List of file or directory paths to analyze
        include_pattern: Optional pattern to filter files (e.g., '*.py')
        show_tree: If True, show hierarchical tree; if False, show summary only
        tokens_only: If True, show only total token count
        threshold: Minimum token count to include in tree (0 = include all)

    Returns:
        Formatted string containing token count information
    """
    # Convert paths to Path objects and resolve them
    resolved_paths = []
    for path_str in paths:
        path = Path(path_str).resolve()
        if not path.exists():
            print(f"Warning: Path does not exist: {path}", file=sys.stderr)
            continue
        resolved_paths.append(path)

    if not resolved_paths:
        raise ValueError("No valid paths provided")

    # Determine the repository root
    repo_root = determine_repo_root(resolved_paths)

    # Discover files to include
    all_files = discover_files(resolved_paths, include_pattern)

    if not all_files:
        return "No files found to analyze."

    # Initialize token counter
    token_counter = TokenCounter()

    # Build token tree
    tree_data = token_counter.build_token_tree(all_files, repo_root, threshold)

    # Format output based on requested mode
    formatter = TokenTreeFormatter()

    if tokens_only:
        # Simple token count output
        return formatter.format_summary(tree_data)
    elif show_tree:
        # Full tree visualization
        return formatter.format_tree(tree_data, repo_root)
    else:
        # Fallback to summary
        return formatter.format_summary(tree_data)

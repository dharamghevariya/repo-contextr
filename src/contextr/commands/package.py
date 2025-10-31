"""
Package repository command implementation
"""

import os
import sys
from pathlib import Path

from ..discovery import discover_files
from ..formatters import RepositoryReportFormatter
from ..git import get_git_info, get_recent_git_files


def package_repository(
    paths: list[str],
    include_pattern: str | None = None,
    recent: bool = False,
    show_tokens: bool = False,
    token_threshold: int = 0,
) -> str:
    """
    Package repository content into a formatted text output.

    Args:
        paths: List of file or directory paths to analyze
        include_pattern: Optional pattern to filter files (e.g., '*.py')
        recent: If True, only include files modified in the last 7 days
        show_tokens: If True, include token counts in the output
        token_threshold: Minimum token count to include (only used if show_tokens=True)

    Returns:
        Formatted string containing repository context
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

    # Get git information - check the actual target directory, not repo_root
    target_path = (
        resolved_paths[0]
        if len(resolved_paths) == 1 and resolved_paths[0].is_dir()
        else repo_root
    )
    git_info = get_git_info(target_path)

    # Identify recent files (modified in git commits within the last 7 days)
    recent_files = get_recent_git_files(target_path, days=7)

    # Filter recent files to only include those that match our discovery criteria
    recent_files = [f for f in recent_files if f in all_files]

    # Determine which files to process based on the recent flag
    files_to_process = recent_files if recent else all_files

    # Use the formatter to generate the report
    formatter = RepositoryReportFormatter()
    return formatter.generate_report(
        repo_root=repo_root,
        git_info=git_info,
        all_files=all_files,
        recent_files=recent_files,
        files_to_process=files_to_process,
        recent_mode=recent,
        show_tokens=show_tokens,
        token_threshold=token_threshold,
    )


def determine_repo_root(paths: list[Path]) -> Path:
    """
    Determine the repository root from the given paths.

    For single file, use its directory.
    For multiple files, find common parent.
    For directories, use the directory itself.
    """
    if len(paths) == 1:
        if paths[0].is_file():
            return paths[0].parent
        else:
            return paths[0]

    # Find common parent for multiple paths
    common_parent = Path(os.path.commonpath([str(p) for p in paths]))
    return common_parent

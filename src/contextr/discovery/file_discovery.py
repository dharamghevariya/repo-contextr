"""
File and directory discovery functionality.
"""

import fnmatch
import sys
from pathlib import Path

from ..config import SKIP_DIRS


def discover_files(paths: list[Path], include_pattern: str | None = None) -> list[Path]:
    """
    Discover all files to process from the given paths.

    Args:
        paths: List of file or directory paths
        include_pattern: Optional pattern to filter files (e.g., '*.py')

    Returns:
        List of file paths to process
    """
    files = []

    for path in paths:
        if path.is_file():
            if should_include_file(path, include_pattern):
                files.append(path)
        elif path.is_dir():
            # find files in directory
            try:
                for file_path in path.rglob("*"):
                    if file_path.is_file() and should_include_file(
                        file_path, include_pattern
                    ):
                        if should_skip_path(file_path):
                            continue
                        files.append(file_path)
            except PermissionError:
                print(f"Permission denied accessing directory: {path}", file=sys.stderr)
                continue

    return files


def should_include_file(file_path: Path, include_pattern: str | None = None) -> bool:
    """Check if a file should be included based on the pattern."""
    if include_pattern:
        return fnmatch.fnmatch(file_path.name, include_pattern)
    return True


def should_skip_path(file_path: Path) -> bool:
    """Check if a path should be skipped (common build/cache directories)."""
    return any(part in SKIP_DIRS for part in file_path.parts)

import os
from pathlib import Path
from typing import List, Optional
from utils.helpers import (discover_files)

def package_repository(paths: List[str], include_pattern: Optional[str] = None) -> str:
    """
    Package repository content into a formatted text output.
    
    Args:
        paths: List of file or directory paths to analyze
        include_pattern: Optional pattern to filter files (e.g., '*.py')
        
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

    # get the repo root
    repo_root = determine_repo_root(resolved_paths)

    # find the files to include
    files_to_process = discover_files(resolved_paths, include_pattern)


def determine_repo_root(paths: List[Path]) -> Path:
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
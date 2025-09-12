"""
Package repository command implementation
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

from ..utils.helpers import (
    discover_files,
    generate_tree_structure,
    get_git_info,
    read_file_content,
    is_binary_file
)


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
    
    # Determine the repository root
    repo_root = determine_repo_root(resolved_paths)
    
    # Discover files to include
    files_to_process = discover_files(resolved_paths, include_pattern)
    
    # Get git information - check the actual target directory, not repo_root
    target_path = resolved_paths[0] if len(resolved_paths) == 1 and resolved_paths[0].is_dir() else repo_root
    git_info = get_git_info(target_path)
    
    # Generate output
    output_parts = []
    
    # Header
    output_parts.append("# Repository Context\n")
    
    # File System Location
    output_parts.append("## File System Location\n")
    output_parts.append(f"{repo_root}\n")
    
    # Git Info
    output_parts.append("## Git Info\n")
    if git_info:
        output_parts.append(f"- Commit: {git_info['commit']}")
        output_parts.append(f"- Branch: {git_info['branch']}")
        output_parts.append(f"- Author: {git_info['author']}")
        output_parts.append(f"- Date: {git_info['date']}\n")
    else:
        output_parts.append("Not a git repository\n")
    
    # Structure
    output_parts.append("## Structure\n")
    structure = generate_tree_structure(files_to_process, repo_root)
    output_parts.append(f"```\n{structure}\n```\n")
    
    # File Contents
    output_parts.append("## File Contents\n")
    
    total_lines = 0
    processed_files = 0
    
    for file_path in sorted(files_to_process):
        try:
            # Skip binary files
            if is_binary_file(file_path):
                print(f"Skipping binary file: {file_path.relative_to(repo_root)}", file=sys.stderr)
                continue
            
            content = read_file_content(file_path)
            if content is None:
                print(f"Skipping file (could not read): {file_path.relative_to(repo_root)}", file=sys.stderr)
                continue
            
            relative_path = file_path.relative_to(repo_root)
            file_extension = file_path.suffix.lstrip('.')
            
            # Determine language for syntax highlighting
            language = get_language_for_extension(file_extension)
            
            output_parts.append(f"### File: {relative_path}")
            output_parts.append(f"```{language}")
            output_parts.append(content)
            output_parts.append("```\n")
            
            total_lines += len(content.splitlines())
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}", file=sys.stderr)
            continue
    
    # Summary
    output_parts.append("## Summary")
    output_parts.append(f"- Total files: {processed_files}")
    output_parts.append(f"- Total lines: {total_lines}")
    
    return "\n".join(output_parts)


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


def get_language_for_extension(extension: str) -> str:
    """Map file extensions to syntax highlighting languages."""
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'jsx',
        'tsx': 'tsx',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'zsh',
        'fish': 'fish',
        'ps1': 'powershell',
        'html': 'html',
        'htm': 'html',
        'xml': 'xml',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'toml': 'toml',
        'ini': 'ini',
        'cfg': 'ini',
        'conf': 'ini',
        'md': 'markdown',
        'markdown': 'markdown',
        'rst': 'rst',
        'txt': 'text',
        'sql': 'sql',
        'dockerfile': 'dockerfile',
        'makefile': 'makefile',
        'r': 'r',
        'rmd': 'rmarkdown',
        'tex': 'latex',
        'vim': 'vim',
        'lua': 'lua',
        'pl': 'perl',
        'pm': 'perl',
    }
    
    return language_map.get(extension.lower(), '')
"""
Package repository command implementation
"""
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict

from ..utils.helpers import (
    discover_files,
    generate_tree_structure,
    get_git_info,
    read_file_content,
    is_binary_file,
    get_recent_git_files,
    get_file_git_timestamp
)


def package_repository(
        paths: List[str], 
        include_pattern: Optional[str] = None,
        recent: bool = False
    ) -> str:
    """
    Package repository content into a formatted text output.
    
    Args:
        paths: List of file or directory paths to analyze
        include_pattern: Optional pattern to filter files (e.g., '*.py')
        recent: If True, only include files modified in the last 7 days
        
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
    target_path = resolved_paths[0] if len(resolved_paths) == 1 and resolved_paths[0].is_dir() else repo_root
    git_info = get_git_info(target_path)
    
    # Identify recent files (modified in git commits within the last 7 days)
    recent_files = get_recent_git_files(target_path, days=7)
    
    # Filter recent files to only include those that match our discovery criteria
    recent_files = [f for f in recent_files if f in all_files]
    
    # Determine which files to process based on the recent flag
    files_to_process = recent_files if recent else all_files
    
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
    
    # File Contents or Recent Changes Section
    recent_stats = {'total_lines': 0, 'processed_files': 0}
    
    if recent:
        # In recent mode: show only recent files under "File Contents"
        output_parts.append("## File Contents\n")
        recent_stats = process_files_section(recent_files, repo_root, output_parts, repo_root)
        total_lines = recent_stats['total_lines']
        processed_files = recent_stats['processed_files']
    else:
        # In normal mode: show recent changes first (if any), then all file contents
        if recent_files and len(recent_files) > 0:
            output_parts.append("## Recent Changes\n")
            recent_stats = process_files_section(recent_files, repo_root, output_parts, repo_root)
        
        output_parts.append("## File Contents\n")
        all_stats = process_files_section(all_files, repo_root, output_parts, repo_root)
        total_lines = all_stats['total_lines']
        processed_files = all_stats['processed_files']
    
    # Summary
    output_parts.append("## Summary")
    output_parts.append(f"- Total files: {processed_files}")
    output_parts.append(f"- Total lines: {total_lines}")
    output_parts.append(f"- Recent files (last 7 days): {len(recent_files)}")
    if recent_files and not recent:
        output_parts.append(f"- Recent files (last 7 days): {recent_stats['processed_files']}")
    
    return "\n".join(output_parts)


def process_files_section(files_list: List[Path], repo_root: Path, output_parts: List[str], git_repo_root: Path) -> dict:
    """
    Process a list of files and add their contents to output_parts.
    
    Args:
        files_list: List of file paths to process
        repo_root: Repository root path for relative path calculation
        output_parts: List to append output content to
        git_repo_root: Git repository root path for timestamp lookup
        
    Returns:
        Dictionary with 'total_lines' and 'processed_files' counts
    """
    total_lines = 0
    processed_files = 0
    
    for file_path in sorted(files_list):
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
            
            # Get git timestamp for the file
            git_timestamp = get_file_git_timestamp(file_path, git_repo_root)
            timestamp_str = f" (Modified: {git_timestamp})" if git_timestamp else ""
            
            # Determine language for syntax highlighting
            language = get_language_for_extension(file_extension)
            
            output_parts.append(f"### File: {relative_path}{timestamp_str}")
            output_parts.append(f"```{language}")
            output_parts.append(content)
            output_parts.append("```\n")
            
            total_lines += len(content.splitlines())
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}", file=sys.stderr)
            continue
    
    return {
        'total_lines': total_lines,
        'processed_files': processed_files
    }


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
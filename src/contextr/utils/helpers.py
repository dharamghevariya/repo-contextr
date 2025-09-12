import fnmatch
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess


def discover_files(paths: List[Path], include_pattern: Optional[str] = None) -> List[Path]:
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
                for file_path in path.rglob('*'):
                    if file_path.is_file() and should_include_file(file_path, include_pattern):
                        if should_skip_path(file_path):
                            continue
                        files.append(file_path)
            except PermissionError as e:
                print(f"Permission denied accessing directory: {path}", file=sys.stderr)
                continue
    
    return files


def should_include_file(file_path: Path, include_pattern: Optional[str] = None) -> bool:
    """Check if a file should be included based on the pattern."""
    if include_pattern:
        return fnmatch.fnmatch(file_path.name, include_pattern)
    return True


def should_skip_path(file_path: Path) -> bool:
    """Check if a path should be skipped (common build/cache directories)."""
    skip_dirs = {
        '.git', '.svn', '.hg',  # Version control
        '__pycache__', '.pytest_cache',  # Python cache
        'node_modules', '.npm',  # Node.js
        '.vscode', '.idea',  # IDE directories
        'build', 'dist', 'target',  # Build directories
        '.env', 'venv', '.venv',  # Virtual environments
        '.mypy_cache', '.tox',  # Python tools
        'coverage', '.coverage',  # Coverage reports
        '.DS_Store', 'Thumbs.db',  # OS files
    }
    
    for part in file_path.parts:
        if part in skip_dirs:
            return True
    
    return False


def generate_tree_structure(files: List[Path], root: Path) -> str:
    """
    Generate a tree structure representation of the files.
    
    Args:
        files: List of file paths
        root: Root directory path
        
    Returns:
        String representation of the directory tree
    """
    tree = {}
    
    for file_path in files:
        try:
            relative_path = file_path.relative_to(root)
            parts = relative_path.parts
            
            current = tree
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


def _format_tree(tree: Dict, prefix: str = "", is_last: bool = True) -> str:
    """Recursively format the tree structure."""
    lines = []
    items = sorted(tree.items(), key=lambda x: (x[1] is not None, x[0]))  # Dirs first, then files
    
    for i, (name, subtree) in enumerate(items):
        is_last_item = i == len(items) - 1
        
        if subtree is None:  # It's a file
            lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}")
        else:  # It's a directory
            lines.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}/")
            extension = "    " if is_last_item else "│   "
            lines.append(_format_tree(subtree, prefix + extension, is_last_item))
    
    return "\n".join(filter(None, lines))


def get_git_info(repo_path: Path) -> Optional[Dict[str, str]]:
    """
    Extract git information from the repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with git info or None if not a git repo
    """
    try:
        # Check if it's a git repository by looking for .git directory
        # Start from the repo_path and traverse up the directory tree
        current = repo_path.resolve()
        git_root = None
        
        while current != current.parent:
            git_dir = current / '.git'
            if git_dir.exists():
                git_root = current
                break
            current = current.parent
        
        if git_root is None:
            return None
        
        # Use git commands to get information
        def run_git_command(cmd: List[str]) -> str:
            try:
                result = subprocess.run(
                    ['git'] + cmd,
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ""
        
        commit = run_git_command(['rev-parse', 'HEAD'])
        branch = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        author = run_git_command(['log', '-1', '--pretty=format:%an <%ae>'])
        date = run_git_command(['log', '-1', '--pretty=format:%cd'])
        
        if not commit:  # No commits yet
            return None
            
        return {
            'commit': commit,
            'branch': branch or 'HEAD',
            'author': author or 'Unknown',
            'date': date or 'Unknown'
        }
        
    except Exception as e:
        print(f"Error getting git info: {e}", file=sys.stderr)
        return None


def read_file_content(file_path: Path) -> Optional[str]:
    """
    Read file content with proper handling of large files and encoding.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string or None if cannot read
    """
    try:
        file_size = file_path.stat().st_size
        max_size = 16 * 1024  # 16KB
        
        # Handle empty files
        if file_size == 0:
            return ""
        
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                if file_size > max_size:
                    # Read first part and add truncation notice
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read(max_size // 4)
                    
                    lines = content.splitlines()
                    if len(lines) > 1:
                        # Remove last potentially incomplete line
                        lines = lines[:-1]
                    
                    content = '\n'.join(lines)
                    content += f"\n\n... [File truncated - showing first {format_file_size(max_size)} of {format_file_size(file_size)}]"
                    break
                else:
                    # Read entire file
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                        break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return content
                
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return None


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary by reading a small chunk and checking if it can be decoded as text.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)  # Read first 8KB
            
            # If chunk is empty, it's likely not binary
            if not chunk:
                return False
            
            # Check for common text encodings
            text_encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
            
            for encoding in text_encodings:
                try:
                    decoded = chunk.decode(encoding)
                    # Additional check: if most characters are printable, it's likely text
                    printable_chars = sum(1 for c in decoded if c.isprintable() or c.isspace())
                    if len(decoded) > 0 and printable_chars / len(decoded) > 0.95:
                        return False  # Successfully decoded with mostly printable chars, likely text
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            # If we couldn't decode with any text encoding, it's likely binary
            return True
                
    except Exception:
        return True  # If we can't read it, treat as binary


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
"""
File content reading and processing functionality.
"""
import sys
from pathlib import Path
from typing import Optional

from ..config import TEXT_ENCODINGS, CHUNK_SIZE, MAX_FILE_SIZE


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
        
        # Handle empty files
        if file_size == 0:
            return ""
        
        # Try different encodings
        content = None
        
        for encoding in TEXT_ENCODINGS:
            try:
                if file_size > MAX_FILE_SIZE:
                    # Read first part and add truncation notice
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read(MAX_FILE_SIZE // 4)
                    
                    lines = content.splitlines()
                    if len(lines) > 1:
                        # Remove last potentially incomplete line
                        lines = lines[:-1]
                    
                    content = '\n'.join(lines)
                    content += f"\n\n... [File truncated - showing first {format_file_size(MAX_FILE_SIZE)} of {format_file_size(file_size)}]"
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
            chunk = f.read(CHUNK_SIZE)  # Read first chunk for binary detection
            
            # If chunk is empty, it's likely not binary
            if not chunk:
                return False
            
            # Check for common text encodings
            for encoding in TEXT_ENCODINGS:
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
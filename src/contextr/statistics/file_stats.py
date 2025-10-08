"""
File statistics calculation and analysis.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..processing import read_file_content, is_binary_file


class FileStatistics:
    """Handles calculation of file statistics and analysis."""
    
    def __init__(self):
        """Initialize the file statistics calculator."""
        pass
    
    def get_file_types_statistics(self, files: List[Path]) -> Dict[str, int]:
        """
        Get statistics about file types (extensions) in the given file list.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Dictionary mapping file extensions to their counts, sorted by count (descending)
        """
        extension_counts = {}
        
        for file_path in files:
            # Skip binary files for statistics
            if is_binary_file(file_path):
                continue
                
            # Get extension without the dot, or 'no extension' for files without extension
            extension = file_path.suffix.lstrip('.') if file_path.suffix else 'no extension'
            extension_counts[extension] = extension_counts.get(extension, 0) + 1
        
        # Sort by count (descending) and return as ordered dict
        return dict(sorted(extension_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_largest_file_info(self, files: List[Path]) -> Optional[Dict[str, Any]]:
        """
        Get information about the largest file (by line count) in the given file list.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Dictionary with 'path' and 'lines' keys, or None if no files processed
        """
        largest_file = None
        max_lines = 0
        
        for file_path in files:
            try:
                # Skip binary files
                if is_binary_file(file_path):
                    continue
                
                content = read_file_content(file_path)
                if content is None:
                    continue
                
                line_count = len(content.splitlines())
                
                if line_count > max_lines:
                    max_lines = line_count
                    largest_file = {
                        'path': file_path,
                        'lines': line_count
                    }
                    
            except Exception:
                continue
        
        return largest_file
    
    def calculate_summary_stats(self, files: List[Path]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for a list of files.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Dictionary containing various file statistics
        """
        total_files = 0
        total_lines = 0
        file_types = self.get_file_types_statistics(files)
        largest_file = self.get_largest_file_info(files)
        
        # Calculate total lines and processed files
        for file_path in files:
            try:
                if is_binary_file(file_path):
                    continue
                
                content = read_file_content(file_path)
                if content is None:
                    continue
                
                total_files += 1
                total_lines += len(content.splitlines())
                
            except Exception:
                continue
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'file_types': file_types,
            'largest_file': largest_file,
            'average_lines': total_lines // total_files if total_files > 0 else 0
        }
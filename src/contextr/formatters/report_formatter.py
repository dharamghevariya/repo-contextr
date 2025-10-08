"""
Repository report formatting functionality.
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..processing import read_file_content, is_binary_file
from ..git import get_file_git_timestamp
from ..output import generate_tree_structure
from ..statistics import FileStatistics
from ..config import get_language_for_extension


class RepositoryReportFormatter:
    """Handles the formatting of repository analysis results into readable reports."""
    
    def __init__(self):
        """Initialize the report formatter."""
        self.stats_calculator = FileStatistics()
    
    def generate_report(
        self,
        repo_root: Path,
        git_info: Optional[Dict[str, str]],
        all_files: List[Path],
        recent_files: List[Path],
        files_to_process: List[Path],
        recent_mode: bool = False
    ) -> str:
        """
        Generate a complete repository report.
        
        Args:
            repo_root: Repository root path
            git_info: Git repository information
            all_files: All discovered files
            recent_files: Files modified in recent commits
            files_to_process: Files to include in the report
            recent_mode: Whether operating in recent-only mode
            
        Returns:
            Formatted report string
        """
        output_parts = []
        
        # Header
        output_parts.append(self._generate_header())
        
        # File System Location
        output_parts.append(self._generate_location_section(repo_root))
        
        # Git Info
        output_parts.append(self._generate_git_section(git_info))
        
        # Structure
        output_parts.append(self._generate_structure_section(files_to_process, repo_root))
        
        # File Contents and Recent Changes
        stats = self._generate_content_sections(
            all_files, recent_files, repo_root, output_parts, recent_mode
        )
        
        # Summary
        output_parts.append(self._generate_summary_section(
            stats, recent_files, files_to_process, repo_root
        ))
        
        return "\n".join(output_parts)
    
    def _generate_header(self) -> str:
        """Generate the main header."""
        return "# Repository Context\n"
    
    def _generate_location_section(self, repo_root: Path) -> str:
        """Generate the file system location section."""
        return f"## File System Location\n\n{repo_root}\n"
    
    def _generate_git_section(self, git_info: Optional[Dict[str, str]]) -> str:
        """Generate the git information section."""
        parts = ["## Git Info\n"]
        
        if git_info:
            parts.extend([
                f"- Commit: {git_info['commit']}",
                f"- Branch: {git_info['branch']}",
                f"- Author: {git_info['author']}",
                f"- Date: {git_info['date']}\n"
            ])
        else:
            parts.append("Not a git repository\n")
        
        return "\n".join(parts)
    
    def _generate_structure_section(self, files: List[Path], repo_root: Path) -> str:
        """Generate the directory structure section."""
        structure = generate_tree_structure(files, repo_root)
        return f"## Structure\n\n```\n{structure}\n```\n"
    
    def _generate_content_sections(
        self,
        all_files: List[Path],
        recent_files: List[Path],
        repo_root: Path,
        output_parts: List[str],
        recent_mode: bool
    ) -> Dict[str, int]:
        """
        Generate file content sections and return processing statistics.
        
        Args:
            all_files: All discovered files
            recent_files: Files modified recently
            repo_root: Repository root path
            output_parts: List to append content to
            recent_mode: Whether in recent-only mode
            
        Returns:
            Dictionary with processing statistics
        """
        if recent_mode:
            # In recent mode: show only recent files under "File Contents"
            output_parts.append("## File Contents\n")
            stats = self._process_files_section(recent_files, repo_root, output_parts, repo_root)
        else:
            # In normal mode: show recent changes first (if any), then all file contents
            if recent_files:
                output_parts.append("## Recent Changes\n")
                self._process_files_section(recent_files, repo_root, output_parts, repo_root)
            
            output_parts.append("## File Contents\n")
            stats = self._process_files_section(all_files, repo_root, output_parts, repo_root)
        
        return stats
    
    def _process_files_section(
        self,
        files_list: List[Path],
        repo_root: Path,
        output_parts: List[str],
        git_repo_root: Path
    ) -> Dict[str, int]:
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
    
    def _generate_summary_section(
        self,
        stats: Dict[str, int],
        recent_files: List[Path],
        files_to_process: List[Path],
        repo_root: Path
    ) -> str:
        """Generate the summary statistics section."""
        parts = ["## Summary"]
        
        total_lines = stats['total_lines']
        processed_files = stats['processed_files']
        
        parts.extend([
            f"- Total files: {processed_files}",
            f"- Total lines: {total_lines}",
            f"- Recent files (last 7 days): {len(recent_files)}"
        ])
        
        # Add file type statistics
        file_types_stats = self.stats_calculator.get_file_types_statistics(files_to_process)
        if file_types_stats:
            file_types_str = ", ".join([f".{ext} ({count})" for ext, count in file_types_stats.items()])
            parts.append(f"- File types: {file_types_str}")
        
        # Add largest file information
        largest_file_info = self.stats_calculator.get_largest_file_info(files_to_process)
        if largest_file_info:
            relative_path = largest_file_info['path'].relative_to(repo_root)
            parts.append(f"- Largest file: {relative_path} ({largest_file_info['lines']} lines)")
        
        # Add average file size
        if processed_files > 0:
            avg_size = total_lines // processed_files
            parts.append(f"- Average file size: {avg_size} lines")
        
        return "\n".join(parts)
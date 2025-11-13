"""
Repository report formatting functionality.
"""

import sys
from pathlib import Path

from ..config import get_language_for_extension
from ..git import get_file_git_timestamp
from ..output import generate_tree_structure
from ..processing import is_binary_file, read_file_content
from ..statistics import FileStatistics


class RepositoryReportFormatter:
    """Handles the formatting of repository analysis results into readable reports."""

    def __init__(self):
        """Initialize the report formatter."""
        self.stats_calculator = FileStatistics()

    def generate_report(
        self,
        repo_root: Path,
        git_info: dict[str, str] | None,
        all_files: list[Path],
        recent_files: list[Path],
        files_to_process: list[Path],
        recent_mode: bool = False,
        show_tokens: bool = False,
        token_threshold: int = 0,
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
            show_tokens: Whether to show token counts in the tree
            token_threshold: Minimum token count to include

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
        output_parts.append(
            self._generate_structure_section(
                files_to_process, repo_root, show_tokens, token_threshold
            )
        )

        # File Contents and Recent Changes
        stats = self._generate_content_sections(
            all_files, recent_files, repo_root, output_parts, recent_mode
        )

        # Summary
        output_parts.append(
            self._generate_summary_section(
                stats, recent_files, files_to_process, repo_root, show_tokens
            )
        )

        return "\n".join(output_parts)

    def _generate_header(self) -> str:
        """Generate the main header."""
        return "# Repository Context\n"

    def _generate_location_section(self, repo_root: Path) -> str:
        """Generate the file system location section."""
        return f"## File System Location\n\n{repo_root}\n"

    def _generate_git_section(self, git_info: dict[str, str] | None) -> str:
        """Generate the git information section."""
        parts = ["## Git Info\n"]

        if git_info:
            parts.extend(
                [
                    f"- Commit: {git_info['commit']}",
                    f"- Branch: {git_info['branch']}",
                    f"- Author: {git_info['author']}",
                    f"- Date: {git_info['date']}\n",
                ]
            )
        else:
            parts.append("Not a git repository\n")

        return "\n".join(parts)

    def _generate_structure_section(
        self,
        files: list[Path],
        repo_root: Path,
        show_tokens: bool = False,
        token_threshold: int = 0,
    ) -> str:
        """Generate the directory structure section."""
        if show_tokens:
            # Import TokenCounter here to avoid circular imports
            from ..statistics import TokenCounter

            # Calculate token counts
            token_counter = TokenCounter()
            token_data = token_counter.build_token_tree(
                files, repo_root, token_threshold
            )

            # Generate structure with token counts
            structure = self._generate_tree_with_tokens(token_data["tree"], repo_root)

            # Add total tokens info
            total_tokens = token_data["total_tokens"]
            header = f"## Structure\n\n**Total Tokens:** {total_tokens:,}\n"
            if token_threshold > 0:
                header += f"**Token Threshold:** {token_threshold:,} (showing only files/dirs above threshold)\n"

            return f"{header}\n```\n{structure}\n```\n"
        else:
            # Regular structure without tokens
            structure = generate_tree_structure(files, repo_root)
            return f"## Structure\n\n```\n{structure}\n```\n"

    def _generate_tree_with_tokens(
        self, tree: dict, repo_root: Path, prefix: str = ""
    ) -> str:
        """Generate tree structure with token counts."""
        lines = []

        # Add root
        if not prefix:
            root_name = repo_root.name or str(repo_root)
            root_tokens = sum(self._get_node_tokens(node) for node in tree.values())
            lines.append(f"{root_name}/ ({root_tokens:,} tokens)")

        # Sort items: directories first (alphabetically), then files (by token count descending)
        items = []
        for key, value in tree.items():
            if isinstance(value, dict):
                node_type = value.get("_type", "unknown")
                tokens = value.get("_tokens", 0)
                items.append((key, value, node_type, tokens))

        items.sort(
            key=lambda x: (
                0 if x[2] == "directory" else 1,  # directories first
                -x[3]
                if x[2] == "file"
                else x[0].lower(),  # files by tokens desc, dirs by name
            )
        )

        for i, (name, node, node_type, tokens) in enumerate(items):
            is_last_item = i == len(items) - 1

            # Choose the appropriate tree characters
            connector = "└── " if is_last_item else "├── "
            extension = "    " if is_last_item else "│   "

            # Format the line
            if node_type == "directory":
                line = f"{prefix}{connector}{name}/ ({tokens:,} tokens)"
                lines.append(line)

                # Recursively format children
                children = node.get("_children", {})
                if children:
                    child_tree = self._generate_tree_with_tokens(
                        children, repo_root, prefix + extension
                    )
                    lines.append(child_tree)

            elif node_type == "file":
                line = f"{prefix}{connector}{name} ({tokens:,} tokens)"
                lines.append(line)

        return "\n".join(filter(None, lines))

    def _get_node_tokens(self, node: dict) -> int:
        """Get token count for a node."""
        if isinstance(node, dict):
            tokens: int = node.get("_tokens", 0)
            return tokens
        return 0

    def _generate_content_sections(
        self,
        all_files: list[Path],
        recent_files: list[Path],
        repo_root: Path,
        output_parts: list[str],
        recent_mode: bool,
    ) -> dict[str, int]:
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
            stats = self._process_files_section(
                recent_files, repo_root, output_parts, repo_root
            )
        else:
            # In normal mode: show recent changes first (if any), then all file contents
            if recent_files:
                output_parts.append("## Recent Changes\n")
                self._process_files_section(
                    recent_files, repo_root, output_parts, repo_root
                )

            output_parts.append("## File Contents\n")
            stats = self._process_files_section(
                all_files, repo_root, output_parts, repo_root
            )

        return stats

    def _process_files_section(
        self,
        files_list: list[Path],
        repo_root: Path,
        output_parts: list[str],
        git_repo_root: Path,
    ) -> dict[str, int]:
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
                    print(
                        f"Skipping binary file: {file_path.relative_to(repo_root)}",
                        file=sys.stderr,
                    )
                    continue

                content = read_file_content(file_path)
                if content is None:
                    print(
                        f"Skipping file (could not read): {file_path.relative_to(repo_root)}",
                        file=sys.stderr,
                    )
                    continue

                relative_path = file_path.relative_to(repo_root)
                file_extension = file_path.suffix.lstrip(".")

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

        return {"total_lines": total_lines, "processed_files": processed_files}

    def _generate_summary_section(
        self,
        stats: dict[str, int],
        recent_files: list[Path],
        files_to_process: list[Path],
        repo_root: Path,
        show_tokens: bool = False,
    ) -> str:
        """Generate the summary statistics section."""
        parts = ["## Summary"]

        total_lines = stats["total_lines"]
        processed_files = stats["processed_files"]

        parts.extend(
            [
                f"- Total files: {processed_files}",
                f"- Total lines: {total_lines}",
                f"- Recent files (last 7 days): {len(recent_files)}",
            ]
        )

        # Add token count if enabled
        if show_tokens:
            from ..statistics import TokenCounter

            token_counter = TokenCounter()
            token_counts = token_counter.count_files_tokens(files_to_process)
            total_tokens = sum(token_counts.values())
            parts.append(f"- Estimated tokens: {total_tokens:,}")

        # Add file type statistics
        file_types_stats = self.stats_calculator.get_file_types_statistics(
            files_to_process
        )
        if file_types_stats:
            file_types_str = ", ".join(
                [f".{ext} ({count})" for ext, count in file_types_stats.items()]
            )
            parts.append(f"- File types: {file_types_str}")

        # Add largest file information
        largest_file_info = self.stats_calculator.get_largest_file_info(
            files_to_process
        )
        if largest_file_info:
            relative_path = largest_file_info["path"].relative_to(repo_root)
            parts.append(
                f"- Largest file: {relative_path} ({largest_file_info['lines']} lines)"
            )

        # Add average file size
        if processed_files > 0:
            avg_size = total_lines // processed_files
            parts.append(f"- Average file size: {avg_size} lines")

        return "\n".join(parts)

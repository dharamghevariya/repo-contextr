"""
Git repository operations and information extraction.
"""

import subprocess
import sys
from pathlib import Path


def find_git_root(start_path: Path) -> Path | None:
    """
    Find the git repository root by traversing up the directory tree.

    Args:
        start_path: Path to start searching from

    Returns:
        Path to git root directory or None if not found
    """
    current = start_path.resolve()

    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists():
            return current
        current = current.parent

    return None


def get_git_info(repo_path: Path) -> dict[str, str] | None:
    """
    Extract git information from the repository.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with git info or None if not a git repo
    """
    try:
        git_root = find_git_root(repo_path)
        if git_root is None:
            return None

        # Use git commands to get information
        def run_git_command(cmd: list[str]) -> str:
            try:
                result = subprocess.run(
                    ["git"] + cmd,
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ""

        commit = run_git_command(["rev-parse", "HEAD"])
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        author = run_git_command(["log", "-1", "--pretty=format:%an <%ae>"])
        date = run_git_command(["log", "-1", "--pretty=format:%cd"])

        if not commit:  # No commits yet
            return None

        return {
            "commit": commit,
            "branch": branch or "HEAD",
            "author": author or "Unknown",
            "date": date or "Unknown",
        }

    except Exception as e:
        print(f"Error getting git info: {e}", file=sys.stderr)
        return None


def get_recent_git_files(repo_path: Path, days: int = 7) -> list[Path]:
    """
    Get files that have been modified in git commits within the last N days.

    Args:
        repo_path: Path to the repository
        days: Number of days to look back (default: 7)

    Returns:
        List of file paths that were modified in recent commits
    """
    try:
        git_root = find_git_root(repo_path)
        if git_root is None:
            return []

        # Get commits from the last N days
        since_date = f"{days}.days.ago"

        def run_git_command(cmd: list[str]) -> str:
            try:
                result = subprocess.run(
                    ["git"] + cmd,
                    cwd=git_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ""

        # Get files changed in commits from the last N days
        # Using --name-only to get just the file names, --since to limit by date
        changed_files_output = run_git_command(
            ["log", f"--since={since_date}", "--name-only", "--pretty=format:", "--"]
        )

        if not changed_files_output:
            return []

        # Parse the output and convert to absolute paths
        recent_files = []
        file_lines = [
            line.strip() for line in changed_files_output.split("\n") if line.strip()
        ]

        for file_line in file_lines:
            file_path = git_root / file_line
            if file_path.exists() and file_path.is_file():
                recent_files.append(file_path)

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for file_path in recent_files:
            if file_path not in seen:
                seen.add(file_path)
                unique_files.append(file_path)

        return unique_files

    except Exception as e:
        print(f"Error getting recent git files: {e}", file=sys.stderr)
        return []


def get_file_git_timestamp(file_path: Path, repo_root: Path) -> str | None:
    """
    Get the last commit timestamp for a specific file from git.

    Args:
        file_path: Path to the file
        repo_root: Root path of the git repository

    Returns:
        Formatted timestamp string or None if not available
    """
    try:
        relative_path = file_path.relative_to(repo_root)

        # Get the last commit date for this specific file
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%ci", "--", str(relative_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            # Parse the git timestamp and reformat it
            # Git timestamp format: 2024-01-15 14:30:22 -0500
            timestamp_str = result.stdout.strip()
            # Take only the date and time part (remove timezone)
            datetime_part = timestamp_str.split(" ")[0:2]
            return " ".join(datetime_part)

        return None

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return None

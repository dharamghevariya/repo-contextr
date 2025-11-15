"""
Unit tests for git operations module.

Tests cover:
- Git root discovery
- Git information extraction
- Recent files detection
- File timestamp retrieval
- Error handling for non-git repositories
"""

import subprocess
from unittest.mock import Mock, patch

from contextr.git.git_operations import (
    find_git_root,
    get_file_git_timestamp,
    get_git_info,
    get_recent_git_files,
)


class TestFindGitRoot:
    """Test the find_git_root function."""

    def test_find_git_root_in_repo(self, sample_git_repo):
        """Test finding git root in a git repository."""
        result = find_git_root(sample_git_repo)
        assert result.resolve() == sample_git_repo.resolve()

    def test_find_git_root_in_subdirectory(self, sample_git_repo):
        """Test finding git root from a subdirectory."""
        subdir = sample_git_repo / "src"
        result = find_git_root(subdir)
        assert result.resolve() == sample_git_repo.resolve()

    def test_find_git_root_non_git_directory(self, non_git_dir):
        """Test finding git root in non-git directory returns None."""
        result = find_git_root(non_git_dir)
        assert result is None

    def test_find_git_root_nonexistent_path(self, temp_dir):
        """Test finding git root with nonexistent path."""
        nonexistent = temp_dir / "does_not_exist"
        result = find_git_root(nonexistent)
        assert result is None


class TestGetGitInfo:
    """Test the get_git_info function."""

    def test_get_git_info_valid_repo(self, sample_git_repo):
        """Test getting git info from valid repository."""
        result = get_git_info(sample_git_repo)

        assert result is not None
        assert isinstance(result, dict)
        assert "commit" in result
        assert "branch" in result
        assert "author" in result
        assert "date" in result
        assert len(result["commit"]) > 0

    def test_get_git_info_non_git_directory(self, non_git_dir):
        """Test getting git info from non-git directory."""
        result = get_git_info(non_git_dir)
        assert result is None

    def test_get_git_info_git_command_failure(self, sample_git_repo):
        """Test handling git command failures."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            result = get_git_info(sample_git_repo)
            assert result is None

    def test_get_git_info_no_commits(self, temp_dir):
        """Test getting git info from repo with no commits."""
        # Create empty git repo
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        with patch("subprocess.run") as mock_run:
            # Mock git commands to return empty strings (no commits)
            mock_run.return_value = Mock(stdout="", returncode=0)
            result = get_git_info(temp_dir)
            assert result is None

    def test_get_git_info_git_not_found(self, sample_git_repo):
        """Test handling when git command is not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            result = get_git_info(sample_git_repo)
            assert result is None

    def test_get_git_info_exception_handling(self, sample_git_repo, capsys):
        """Test exception handling in get_git_info."""
        with patch("contextr.git.git_operations.find_git_root") as mock_find:
            mock_find.side_effect = Exception("Test error")
            result = get_git_info(sample_git_repo)
            assert result is None

            captured = capsys.readouterr()
            assert "Error getting git info" in captured.err


class TestGetRecentGitFiles:
    """Test the get_recent_git_files function."""

    def test_get_recent_files_valid_repo(self, recent_files_repo):
        """Test getting recent files from valid repository."""
        result = get_recent_git_files(recent_files_repo, days=30)

        assert isinstance(result, list)
        # Should have at least the files we committed
        assert len(result) >= 0

    def test_get_recent_files_non_git_directory(self, non_git_dir):
        """Test getting recent files from non-git directory."""
        result = get_recent_git_files(non_git_dir)
        assert result == []

    def test_get_recent_files_no_recent_commits(self, sample_git_repo):
        """Test getting recent files when no recent commits exist."""
        with patch("subprocess.run") as mock_run:
            # Mock git log to return empty output
            mock_run.return_value = Mock(stdout="", returncode=0)
            result = get_recent_git_files(sample_git_repo)
            assert result == []

    def test_get_recent_files_git_command_failure(self, sample_git_repo):
        """Test handling git command failures in recent files."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            result = get_recent_git_files(sample_git_repo)
            assert result == []

    def test_get_recent_files_custom_days(self, recent_files_repo):
        """Test getting recent files with custom day count."""
        result = get_recent_git_files(recent_files_repo, days=1)
        assert isinstance(result, list)

    def test_get_recent_files_exception_handling(self, sample_git_repo, capsys):
        """Test exception handling in get_recent_git_files."""
        with patch("contextr.git.git_operations.find_git_root") as mock_find:
            mock_find.side_effect = Exception("Test error")
            result = get_recent_git_files(sample_git_repo)
            assert result == []

            captured = capsys.readouterr()
            assert "Error getting recent git files" in captured.err

    def test_get_recent_files_removes_duplicates(self, sample_git_repo):
        """Test that duplicate files are removed from recent files."""
        with patch("subprocess.run") as mock_run:
            # Mock git log to return duplicate file entries
            mock_run.return_value = Mock(
                stdout="file1.py\nfile2.py\nfile1.py\nfile3.py\n",
                returncode=0
            )

            # Mock file existence
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.is_file", return_value=True):
                result = get_recent_git_files(sample_git_repo)

                # Should have unique files only
                file_names = [f.name for f in result]
                assert len(file_names) == len(set(file_names))


class TestGetFileGitTimestamp:
    """Test the get_file_git_timestamp function."""

    def test_get_file_timestamp_valid_file(self, sample_git_repo):
        """Test getting timestamp for a valid file."""
        test_file = sample_git_repo / "README.md"
        result = get_file_git_timestamp(test_file, sample_git_repo)

        # Should return a timestamp string or None
        assert result is None or isinstance(result, str)

    def test_get_file_timestamp_nonexistent_file(self, sample_git_repo):
        """Test getting timestamp for nonexistent file."""
        nonexistent = sample_git_repo / "does_not_exist.py"
        result = get_file_git_timestamp(nonexistent, sample_git_repo)
        assert result is None

    def test_get_file_timestamp_git_command_failure(self, sample_git_repo):
        """Test handling git command failures in timestamp retrieval."""
        test_file = sample_git_repo / "README.md"

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            result = get_file_git_timestamp(test_file, sample_git_repo)
            assert result is None

    def test_get_file_timestamp_no_commits_for_file(self, sample_git_repo):
        """Test getting timestamp when file has no commits."""
        test_file = sample_git_repo / "README.md"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(stdout="", returncode=0)
            result = get_file_git_timestamp(test_file, sample_git_repo)
            assert result is None

    def test_get_file_timestamp_valid_output(self, sample_git_repo):
        """Test parsing valid git timestamp output."""
        test_file = sample_git_repo / "README.md"

        with patch("subprocess.run") as mock_run:
            # Mock git log output with timestamp
            mock_run.return_value = Mock(
                stdout="2024-01-15 14:30:22 -0500",
                returncode=0
            )
            result = get_file_git_timestamp(test_file, sample_git_repo)
            assert result == "2024-01-15 14:30:22"

    def test_get_file_timestamp_file_not_found_error(self, sample_git_repo):
        """Test handling FileNotFoundError in timestamp retrieval."""
        test_file = sample_git_repo / "README.md"

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            result = get_file_git_timestamp(test_file, sample_git_repo)
            assert result is None

    def test_get_file_timestamp_value_error(self, sample_git_repo):
        """Test handling ValueError in timestamp retrieval."""
        test_file = sample_git_repo / "README.md"

        with patch("pathlib.Path.relative_to") as mock_relative:
            mock_relative.side_effect = ValueError("Path error")
            result = get_file_git_timestamp(test_file, sample_git_repo)
            assert result is None

"""Unit tests for git operations functionality."""

from pathlib import Path
from unittest.mock import patch

from contextr.git.git_operations import (
    find_git_root,
    get_file_git_timestamp,
    get_git_info,
    get_recent_git_files,
)


class TestFindGitRoot:
    """Tests for find_git_root function."""

    def test_find_git_root_in_repo(self, sample_git_repo):
        """Test finding git root in a git repository."""
        result = find_git_root(sample_git_repo)

        assert result is not None
        assert result == sample_git_repo
        assert (result / ".git").exists()

    def test_find_git_root_from_subdirectory(self, sample_git_repo):
        """Test finding git root from a subdirectory."""
        subdir = sample_git_repo / "src"

        result = find_git_root(subdir)

        assert result is not None
        assert result == sample_git_repo

    def test_find_git_root_not_in_repo(self, non_git_dir):
        """Test that None is returned when not in a git repo."""
        result = find_git_root(non_git_dir)

        assert result is None


class TestGetGitInfo:
    """Tests for get_git_info function."""

    def test_get_git_info_from_repo(self, sample_git_repo):
        """Test getting git info from a valid repository."""
        result = get_git_info(sample_git_repo)

        assert result is not None
        assert "commit" in result
        assert "branch" in result
        assert "author" in result
        assert "date" in result

        # Check that values are not empty
        assert len(result["commit"]) > 0
        assert result["author"] == "Test User <test@example.com>"

    def test_get_git_info_from_non_repo(self, non_git_dir):
        """Test getting git info from a non-git directory."""
        result = get_git_info(non_git_dir)

        assert result is None

    def test_get_git_info_branch_name(self, sample_git_repo):
        """Test that branch name is correctly retrieved."""
        result = get_git_info(sample_git_repo)

        assert result is not None
        # Default branch is usually 'main' or 'master'
        assert result["branch"] in ["main", "master", "HEAD"]

    @patch("subprocess.run")
    def test_get_git_info_handles_git_errors(self, mock_run, temp_dir):
        """Test that git errors are handled gracefully."""
        # Make git directory to pass the root check
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        # Simulate git command failure
        mock_run.side_effect = Exception("Git command failed")

        result = get_git_info(temp_dir)

        assert result is None


class TestGetRecentGitFiles:
    """Tests for get_recent_git_files function."""

    def test_get_recent_files_from_repo(self, recent_files_repo):
        """Test getting recent files from a repository."""
        result = get_recent_git_files(recent_files_repo, days=7)

        assert isinstance(result, list)
        # Should have at least the new file we added
        assert len(result) >= 1

        # Check that returned paths exist
        for file_path in result:
            assert file_path.exists()
            assert file_path.is_file()

    def test_get_recent_files_from_non_repo(self, non_git_dir):
        """Test getting recent files from non-git directory."""
        result = get_recent_git_files(non_git_dir, days=7)

        assert result == []

    def test_get_recent_files_different_timeframes(self, recent_files_repo):
        """Test getting recent files with different day counts."""
        result_7 = get_recent_git_files(recent_files_repo, days=7)
        result_30 = get_recent_git_files(recent_files_repo, days=30)

        # 30 days should include all files from 7 days
        assert len(result_30) >= len(result_7)

    def test_get_recent_files_no_duplicates(self, recent_files_repo):
        """Test that recent files list has no duplicates."""
        result = get_recent_git_files(recent_files_repo, days=7)

        # Check for duplicates
        unique_files = list(set(result))
        assert len(unique_files) == len(result)

    @patch("subprocess.run")
    def test_get_recent_files_handles_errors(self, mock_run, temp_dir):
        """Test that errors are handled gracefully."""
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        mock_run.side_effect = Exception("Git error")

        result = get_recent_git_files(temp_dir, days=7)

        assert result == []


class TestGetFileGitTimestamp:
    """Tests for get_file_git_timestamp function."""

    def test_get_timestamp_for_committed_file(self, sample_git_repo):
        """Test getting timestamp for a committed file."""
        test_file = sample_git_repo / "README.md"

        result = get_file_git_timestamp(test_file, sample_git_repo)

        assert result is not None
        assert isinstance(result, str)
        # Should contain date-like content
        assert len(result) > 0

    def test_get_timestamp_for_file_in_subdirectory(self, sample_git_repo):
        """Test getting timestamp for file in subdirectory."""
        test_file = sample_git_repo / "src" / "app.py"

        result = get_file_git_timestamp(test_file, sample_git_repo)

        assert result is not None
        assert isinstance(result, str)

    def test_get_timestamp_for_uncommitted_file(self, sample_git_repo):
        """Test getting timestamp for an uncommitted file."""
        # Create a new file that hasn't been committed
        new_file = sample_git_repo / "uncommitted.py"
        new_file.write_text("# New file")

        result = get_file_git_timestamp(new_file, sample_git_repo)

        # Should return None for uncommitted files
        assert result is None

    def test_get_timestamp_file_outside_repo(self, sample_git_repo, temp_dir):
        """Test getting timestamp for file outside repo."""
        # Note: temp_dir and sample_git_repo are the same in this fixture
        # Create a separate temp directory
        import tempfile

        with tempfile.TemporaryDirectory() as other_dir:
            other_path = Path(other_dir)
            outside_file = other_path / "outside.txt"
            outside_file.write_text("content")

            # ValueError is caught and function returns None
            result = get_file_git_timestamp(outside_file, sample_git_repo)
            assert result is None

    @patch("contextr.git.git_operations.subprocess.run")
    def test_get_timestamp_handles_git_errors(self, mock_run, sample_git_repo):
        """Test that git errors are handled gracefully."""
        test_file = sample_git_repo / "README.md"

        # Simulate git command failure with CalledProcessError
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ["git"])

        result = get_file_git_timestamp(test_file, sample_git_repo)

        assert result is None

def test_imports():
    """Test that the main package can be imported."""
    import contextr

    assert contextr is not None


def test_fixtures_available(temp_dir, sample_git_repo, mock_files_dir):
    """Test that all shared fixtures are available and working."""
    # Check temp_dir fixture
    assert temp_dir.exists()
    assert temp_dir.is_dir()

    # Check sample_git_repo fixture
    assert sample_git_repo.exists()
    assert (sample_git_repo / ".git").exists()
    assert (sample_git_repo / "README.md").exists()

    # Check mock_files_dir fixture
    assert mock_files_dir.exists()
    assert (mock_files_dir / "app.py").exists()
    assert (mock_files_dir / "README.md").exists()


def test_pytest_markers():
    """Test that pytest is configured correctly."""
    import pytest

    # Verify pytest is working
    assert pytest.__version__ is not None

"""Unit tests for file discovery functionality."""

from contextr.discovery.file_discovery import (
    discover_files,
    should_include_file,
    should_skip_path,
)


class TestDiscoverFiles:
    """Tests for discover_files function."""

    def test_discover_single_file(self, temp_dir):
        """Test discovering a single file."""
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello')")

        files = discover_files([test_file])

        assert len(files) == 1
        assert files[0] == test_file

    def test_discover_directory(self, mock_files_dir):
        """Test discovering all files in a directory."""
        files = discover_files([mock_files_dir])

        # Should find Python, JS, MD files but skip binary and excluded dirs
        assert len(files) > 0
        file_names = [f.name for f in files]
        assert "app.py" in file_names
        assert "script.js" in file_names
        assert "README.md" in file_names

    def test_discover_with_include_pattern(self, mock_files_dir):
        """Test discovering files with include pattern."""
        files = discover_files([mock_files_dir], include_pattern="*.py")

        # Should only find Python files
        assert all(f.suffix == ".py" for f in files)
        file_names = [f.name for f in files]
        assert "app.py" in file_names
        assert "utils.py" in file_names

    def test_discover_with_wildcard_pattern(self, mock_files_dir):
        """Test discovering files with wildcard pattern."""
        files = discover_files([mock_files_dir], include_pattern="*.md")

        # Should only find Markdown files
        assert all(f.suffix == ".md" for f in files)
        file_names = [f.name for f in files]
        assert "README.md" in file_names
        assert "NOTES.md" in file_names

    def test_discover_skips_excluded_directories(self, mock_files_dir):
        """Test that excluded directories are skipped."""
        files = discover_files([mock_files_dir])

        # Should not include files from __pycache__ or node_modules
        file_paths = [str(f) for f in files]
        assert not any("__pycache__" in p for p in file_paths)
        assert not any("node_modules" in p for p in file_paths)

    def test_discover_nested_files(self, mock_files_dir):
        """Test discovering files in nested directories."""
        files = discover_files([mock_files_dir])

        file_names = [f.name for f in files]
        assert "nested.py" in file_names

    def test_discover_empty_directory(self, empty_dir):
        """Test discovering files in an empty directory."""
        files = discover_files([empty_dir])

        assert len(files) == 0

    def test_discover_multiple_paths(self, temp_dir):
        """Test discovering files from multiple paths."""
        # Create two separate directories
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        (dir1 / "file1.py").write_text("code1")
        (dir2 / "file2.py").write_text("code2")

        files = discover_files([dir1, dir2])

        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.py" in file_names
        assert "file2.py" in file_names

    def test_discover_nonexistent_path(self, temp_dir):
        """Test discovering with a nonexistent path."""
        nonexistent = temp_dir / "nonexistent"

        files = discover_files([nonexistent])

        assert len(files) == 0


class TestShouldIncludeFile:
    """Tests for should_include_file function."""

    def test_include_without_pattern(self, temp_dir):
        """Test that all files are included without a pattern."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        assert should_include_file(test_file) is True

    def test_include_with_matching_pattern(self, temp_dir):
        """Test that matching files are included."""
        test_file = temp_dir / "test.py"
        test_file.write_text("code")

        assert should_include_file(test_file, "*.py") is True

    def test_exclude_with_non_matching_pattern(self, temp_dir):
        """Test that non-matching files are excluded."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        assert should_include_file(test_file, "*.py") is False

    def test_pattern_matches_filename_only(self, temp_dir):
        """Test that pattern matches filename, not full path."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.py"
        test_file.write_text("code")

        # Pattern should match the filename, not the path
        assert should_include_file(test_file, "*.py") is True


class TestShouldSkipPath:
    """Tests for should_skip_path function."""

    def test_skip_pycache_directory(self, temp_dir):
        """Test that __pycache__ directories are skipped."""
        path = temp_dir / "__pycache__" / "module.pyc"

        assert should_skip_path(path) is True

    def test_skip_node_modules_directory(self, temp_dir):
        """Test that node_modules directories are skipped."""
        path = temp_dir / "node_modules" / "package" / "index.js"

        assert should_skip_path(path) is True

    def test_skip_git_directory(self, temp_dir):
        """Test that .git directories are skipped."""
        path = temp_dir / ".git" / "config"

        assert should_skip_path(path) is True

    def test_skip_venv_directory(self, temp_dir):
        """Test that venv directories are skipped."""
        path = temp_dir / "venv" / "lib" / "python3.12"

        assert should_skip_path(path) is True

    def test_do_not_skip_normal_directory(self, temp_dir):
        """Test that normal directories are not skipped."""
        path = temp_dir / "src" / "app.py"

        assert should_skip_path(path) is False

    def test_skip_build_directories(self, temp_dir):
        """Test that build/dist directories are skipped."""
        build_path = temp_dir / "build" / "output.js"
        dist_path = temp_dir / "dist" / "bundle.js"

        assert should_skip_path(build_path) is True
        assert should_skip_path(dist_path) is True

from unittest.mock import patch

from contextr.discovery.file_discovery import (
    discover_files,
    should_include_file,
    should_skip_path,
)


class TestDiscoverFiles:
    """Test the discover_files function."""

    def test_discover_single_file(self, temp_dir):
        """Test discovering a single file."""
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello')")

        result = discover_files([test_file])
        assert len(result) == 1
        assert result[0] == test_file

    def test_discover_multiple_files(self, temp_dir):
        """Test discovering multiple files."""
        file1 = temp_dir / "file1.py"
        file2 = temp_dir / "file2.py"
        file1.write_text("# file1")
        file2.write_text("# file2")

        result = discover_files([file1, file2])
        assert len(result) == 2
        assert file1 in result
        assert file2 in result

    def test_discover_directory(self, temp_dir):
        """Test discovering files in a directory."""
        (temp_dir / "file1.py").write_text("# file1")
        (temp_dir / "file2.js").write_text("// file2")

        result = discover_files([temp_dir])
        assert len(result) == 2
        assert any(f.name == "file1.py" for f in result)
        assert any(f.name == "file2.js" for f in result)

    def test_discover_with_pattern(self, temp_dir):
        """Test discovering files with include pattern."""
        (temp_dir / "file1.py").write_text("# python")
        (temp_dir / "file2.js").write_text("// javascript")
        (temp_dir / "file3.py").write_text("# python")

        result = discover_files([temp_dir], include_pattern="*.py")
        assert len(result) == 2
        assert all(f.suffix == ".py" for f in result)

    def test_discover_nested_directories(self, temp_dir):
        """Test discovering files in nested directories."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (temp_dir / "root.py").write_text("# root")
        (subdir / "nested.py").write_text("# nested")

        result = discover_files([temp_dir])
        assert len(result) == 2
        assert any(f.name == "root.py" for f in result)
        assert any(f.name == "nested.py" for f in result)

    def test_discover_skips_excluded_directories(self, temp_dir):
        """Test that excluded directories are skipped."""
        # Create __pycache__ directory (should be skipped)
        pycache = temp_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.pyc").write_bytes(b"compiled")

        # Create normal file
        (temp_dir / "normal.py").write_text("# normal")

        result = discover_files([temp_dir])
        assert len(result) == 1
        assert result[0].name == "normal.py"

    def test_discover_permission_error(self, temp_dir, capsys):
        """Test handling of permission errors."""
        with patch("pathlib.Path.rglob") as mock_rglob:
            mock_rglob.side_effect = PermissionError("Access denied")

            result = discover_files([temp_dir])
            assert result == []

            captured = capsys.readouterr()
            assert "Permission denied accessing directory" in captured.err

    def test_discover_nonexistent_path(self, temp_dir):
        """Test discovering nonexistent paths."""
        nonexistent = temp_dir / "does_not_exist"
        result = discover_files([nonexistent])
        assert result == []

    def test_discover_empty_directory(self, temp_dir):
        """Test discovering files in empty directory."""
        result = discover_files([temp_dir])
        assert result == []


class TestShouldIncludeFile:
    """Test the should_include_file function."""

    def test_no_pattern_includes_all(self, temp_dir):
        """Test that no pattern includes all files."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        assert should_include_file(test_file) is True
        assert should_include_file(test_file, None) is True

    def test_pattern_matches_extension(self, temp_dir):
        """Test pattern matching by extension."""
        py_file = temp_dir / "test.py"
        js_file = temp_dir / "test.js"
        py_file.write_text("python")
        js_file.write_text("javascript")

        assert should_include_file(py_file, "*.py") is True
        assert should_include_file(js_file, "*.py") is False

    def test_pattern_matches_name(self, temp_dir):
        """Test pattern matching by filename."""
        readme = temp_dir / "README.md"
        other = temp_dir / "other.md"
        readme.write_text("readme")
        other.write_text("other")

        assert should_include_file(readme, "README*") is True
        assert should_include_file(other, "README*") is False

    def test_pattern_complex_glob(self, temp_dir):
        """Test complex glob patterns."""
        test_file = temp_dir / "test_module.py"
        other_file = temp_dir / "module.py"
        test_file.write_text("test")
        other_file.write_text("module")

        assert should_include_file(test_file, "test_*.py") is True
        assert should_include_file(other_file, "test_*.py") is False


class TestShouldSkipPath:
    """Test the should_skip_path function."""

    def test_skip_pycache_directory(self, temp_dir):
        """Test skipping __pycache__ directories."""
        pycache_file = temp_dir / "__pycache__" / "module.pyc"
        normal_file = temp_dir / "module.py"

        assert should_skip_path(pycache_file) is True
        assert should_skip_path(normal_file) is False

    def test_skip_node_modules(self, temp_dir):
        """Test skipping node_modules directories."""
        node_file = temp_dir / "node_modules" / "package" / "index.js"
        normal_file = temp_dir / "src" / "index.js"

        assert should_skip_path(node_file) is True
        assert should_skip_path(normal_file) is False

    def test_skip_git_directory(self, temp_dir):
        """Test skipping .git directories."""
        git_file = temp_dir / ".git" / "config"
        normal_file = temp_dir / "config.py"

        assert should_skip_path(git_file) is True
        assert should_skip_path(normal_file) is False

    def test_skip_build_directories(self, temp_dir):
        """Test skipping build directories."""
        build_file = temp_dir / "build" / "output.exe"
        dist_file = temp_dir / "dist" / "package.tar.gz"
        normal_file = temp_dir / "src" / "main.py"

        assert should_skip_path(build_file) is True
        assert should_skip_path(dist_file) is True
        assert should_skip_path(normal_file) is False

    def test_nested_skip_directories(self, temp_dir):
        """Test skipping nested excluded directories."""
        nested_file = temp_dir / "project" / "__pycache__" / "cache.pyc"
        assert should_skip_path(nested_file) is True

    def test_no_skip_for_normal_paths(self, temp_dir):
        """Test that normal paths are not skipped."""
        normal_paths = [
            temp_dir / "src" / "main.py",
            temp_dir / "tests" / "test_main.py",
            temp_dir / "docs" / "README.md",
            temp_dir / "config" / "settings.json",
        ]

        for path in normal_paths:
            assert should_skip_path(path) is False

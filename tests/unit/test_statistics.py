"""Unit tests for file statistics functionality."""

import pytest

from contextr.statistics.file_stats import FileStatistics


class TestFileStatistics:
    """Tests for FileStatistics class."""

    @pytest.fixture
    def stats_calculator(self):
        """Create a FileStatistics instance."""
        return FileStatistics()

    def test_get_file_types_statistics(self, stats_calculator, mock_files_dir):
        """Test getting file type statistics."""
        files = list(mock_files_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.get_file_types_statistics(files)

        assert isinstance(result, dict)
        assert "py" in result
        assert "md" in result
        assert "js" in result
        # Should count Python files
        assert result["py"] >= 2

    def test_get_file_types_statistics_empty_list(self, stats_calculator):
        """Test file type statistics with empty file list."""
        result = stats_calculator.get_file_types_statistics([])

        assert result == {}

    def test_get_file_types_statistics_sorted_by_count(
        self, stats_calculator, temp_dir
    ):
        """Test that file types are sorted by count."""
        # Create files with different counts
        for i in range(5):
            (temp_dir / f"file{i}.py").write_text("code")
        for i in range(3):
            (temp_dir / f"doc{i}.md").write_text("doc")
        (temp_dir / "script.js").write_text("js")

        files = list(temp_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.get_file_types_statistics(files)

        # Should be sorted by count (descending)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)
        # Python should be first (5 files)
        assert list(result.keys())[0] == "py"

    def test_get_file_types_skips_binary_files(self, stats_calculator, mock_files_dir):
        """Test that binary files are skipped in statistics."""
        files = list(mock_files_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.get_file_types_statistics(files)

        # PNG files should be skipped (they're binary)
        assert "png" not in result

    def test_get_largest_file_info(self, stats_calculator, temp_dir):
        """Test getting largest file information."""
        # Create files of different sizes
        (temp_dir / "small.txt").write_text("short")
        (temp_dir / "medium.txt").write_text("line1\nline2\nline3")
        large_content = "\n".join([f"line {i}" for i in range(100)])
        (temp_dir / "large.txt").write_text(large_content)

        files = list(temp_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.get_largest_file_info(files)

        assert result is not None
        assert "path" in result
        assert "lines" in result
        assert result["path"].name == "large.txt"
        assert result["lines"] == 100

    def test_get_largest_file_info_empty_list(self, stats_calculator):
        """Test largest file info with empty list."""
        result = stats_calculator.get_largest_file_info([])

        assert result is None

    def test_get_largest_file_info_skips_binary(self, stats_calculator, temp_dir):
        """Test that binary files are skipped when finding largest."""
        (temp_dir / "text.txt").write_text("line1\nline2\nline3")
        (temp_dir / "binary.bin").write_bytes(b"\x00" * 1000)

        files = list(temp_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.get_largest_file_info(files)

        assert result is not None
        assert result["path"].name == "text.txt"

    def test_calculate_summary_stats(self, stats_calculator, temp_dir):
        """Test calculating comprehensive summary statistics."""
        # Create various files
        (temp_dir / "file1.py").write_text("line1\nline2\nline3")
        (temp_dir / "file2.py").write_text("line1\nline2")
        (temp_dir / "file3.md").write_text("doc line")

        files = list(temp_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.calculate_summary_stats(files)

        assert "total_files" in result
        assert "total_lines" in result
        assert "file_types" in result
        assert "largest_file" in result
        assert "average_lines" in result

        assert result["total_files"] == 3
        assert result["total_lines"] == 6  # 3 + 2 + 1
        assert result["average_lines"] == 2  # 6 // 3

    def test_calculate_summary_stats_empty_list(self, stats_calculator):
        """Test summary stats with empty file list."""
        result = stats_calculator.calculate_summary_stats([])

        assert result["total_files"] == 0
        assert result["total_lines"] == 0
        assert result["average_lines"] == 0
        assert result["largest_file"] is None

    def test_calculate_summary_stats_file_types(self, stats_calculator, temp_dir):
        """Test that file types are included in summary stats."""
        (temp_dir / "file1.py").write_text("code")
        (temp_dir / "file2.py").write_text("code")
        (temp_dir / "doc.md").write_text("doc")

        files = list(temp_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        result = stats_calculator.calculate_summary_stats(files)

        assert "py" in result["file_types"]
        assert "md" in result["file_types"]
        assert result["file_types"]["py"] == 2
        assert result["file_types"]["md"] == 1

    def test_calculate_summary_stats_handles_errors(self, stats_calculator, temp_dir):
        """Test that summary stats handles file read errors gracefully."""
        # Create a file and then make it unreadable (simulate)
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        # Create a list with valid and potentially problematic files
        files = [test_file]

        # Should not raise exception
        result = stats_calculator.calculate_summary_stats(files)

        assert isinstance(result, dict)
        assert "total_files" in result

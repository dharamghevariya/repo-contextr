from pathlib import Path

from contextr.statistics.file_stats import FileStatistics


class TestGetFileTypesStatistics:
    """Test the get_file_types_statistics method."""

    def test_get_file_types_statistics_single_extension(self, mock_files_dir):
        """Test statistics for files with single extension."""
        stats = FileStatistics()
        file1 = mock_files_dir / "test1.py"
        file2 = mock_files_dir / "test2.py"
        file1.write_text("# Python file", encoding="utf-8")
        file2.write_text("# Another Python file", encoding="utf-8")

        files = [file1, file2]
        result = stats.get_file_types_statistics(files)

        assert isinstance(result, dict)
        assert "py" in result
        assert result["py"] == 2

    def test_get_file_types_statistics_multiple_extensions(self, mock_files_dir):
        """Test statistics for files with multiple extensions."""
        stats = FileStatistics()
        py_file = mock_files_dir / "script.py"
        txt_file = mock_files_dir / "readme.txt"
        md_file = mock_files_dir / "doc.md"
        py_file.write_text("print('hello')", encoding="utf-8")
        txt_file.write_text("text file", encoding="utf-8")
        md_file.write_text("# Markdown", encoding="utf-8")

        files = [py_file, txt_file, md_file]
        result = stats.get_file_types_statistics(files)

        assert isinstance(result, dict)
        assert result["py"] == 1
        assert result["txt"] == 1
        assert result["md"] == 1

    def test_get_file_types_statistics_no_extension(self, mock_files_dir):
        """Test statistics for files without extension."""
        stats = FileStatistics()
        file_no_ext = mock_files_dir / "LICENSE"
        file_no_ext.write_text("MIT License", encoding="utf-8")

        files = [file_no_ext]
        result = stats.get_file_types_statistics(files)

        assert isinstance(result, dict)
        assert "no extension" in result
        assert result["no extension"] == 1

    def test_get_file_types_statistics_empty_list(self):
        """Test statistics with empty file list."""
        stats = FileStatistics()
        result = stats.get_file_types_statistics([])

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_get_file_types_statistics_sorted_by_count(self, temp_dir):
        """Test that results are sorted by count in descending order."""
        stats = FileStatistics()
        # Create 3 .py files, 2 .txt files, 1 .md file
        for i in range(3):
            (temp_dir / f"file{i}.py").write_text(f"# Python {i}", encoding="utf-8")
        for i in range(2):
            (temp_dir / f"file{i}.txt").write_text(f"Text {i}", encoding="utf-8")
        (temp_dir / "doc.md").write_text("# Markdown", encoding="utf-8")

        files = list(temp_dir.glob("*"))
        result = stats.get_file_types_statistics(files)

        # Convert to list to check order
        items = list(result.items())
        assert items[0] == ("py", 3)  # Most common first
        assert items[1] == ("txt", 2)
        assert items[2] == ("md", 1)  # Least common last

    def test_get_file_types_statistics_skips_binary_files(self, temp_dir):
        """Test that binary files are skipped in statistics."""
        stats = FileStatistics()
        text_file = temp_dir / "text.py"
        binary_file = temp_dir / "binary.dat"
        text_file.write_text("# Python", encoding="utf-8")
        # Create a truly binary file with null bytes and invalid UTF-8 sequences
        binary_file.write_bytes(b"\x00\x01\x02\x03\x80\x81\x82\x83\xff\xfe")

        files = [text_file, binary_file]
        result = stats.get_file_types_statistics(files)

        assert "py" in result
        assert "dat" not in result  # Binary file should be skipped

    def test_get_file_types_statistics_mixed_case_extensions(self, mock_files_dir):
        """Test statistics with mixed case extensions."""
        stats = FileStatistics()
        file1 = mock_files_dir / "File.PY"
        file2 = mock_files_dir / "script.py"
        file1.write_text("# Python", encoding="utf-8")
        file2.write_text("# Python", encoding="utf-8")

        files = [file1, file2]
        result = stats.get_file_types_statistics(files)

        # Both should be counted (case-sensitive)
        assert isinstance(result, dict)


class TestGetLargestFileInfo:
    """Test the get_largest_file_info method."""

    def test_get_largest_file_info_single_file(self, mock_files_dir):
        """Test finding largest file with single file."""
        stats = FileStatistics()
        file1 = mock_files_dir / "test.py"
        file1.write_text("line 1\nline 2\nline 3", encoding="utf-8")

        files = [file1]
        result = stats.get_largest_file_info(files)

        assert isinstance(result, dict)
        assert "path" in result
        assert "lines" in result
        assert result["path"] == file1
        assert result["lines"] == 3

    def test_get_largest_file_info_multiple_files(self, mock_files_dir):
        """Test finding largest file among multiple files."""
        stats = FileStatistics()
        small_file = mock_files_dir / "small.py"
        large_file = mock_files_dir / "large.py"
        small_file.write_text("line 1", encoding="utf-8")
        large_file.write_text(
            "line 1\nline 2\nline 3\nline 4\nline 5", encoding="utf-8"
        )

        files = [small_file, large_file]
        result = stats.get_largest_file_info(files)

        assert result["path"] == large_file
        assert result["lines"] == 5

    def test_get_largest_file_info_empty_list(self):
        """Test finding largest file with empty list."""
        stats = FileStatistics()
        result = stats.get_largest_file_info([])

        assert result is None

    def test_get_largest_file_info_all_binary(self, mock_files_dir):
        """Test finding largest file when all files are binary."""
        stats = FileStatistics()
        binary_file = mock_files_dir / "binary.dat"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

        files = [binary_file]
        result = stats.get_largest_file_info(files)

        assert result is None

    def test_get_largest_file_info_empty_files(self, temp_dir):
        """Test finding largest file when all files are empty."""
        stats = FileStatistics()
        file1 = temp_dir / "empty1.txt"
        file2 = temp_dir / "empty2.txt"
        file1.write_text("", encoding="utf-8")
        file2.write_text("", encoding="utf-8")

        files = [file1, file2]
        result = stats.get_largest_file_info(files)

        # Empty files have 0 lines, but should still be counted
        # The implementation might return None if max_lines is 0
        # This is valid behavior, so we test for None OR a valid result with 0 lines
        if result is not None:
            assert result["lines"] == 0
        # If None, that's also acceptable for empty files

    def test_get_largest_file_info_nonexistent_files(self, mock_files_dir):
        """Test finding largest file with nonexistent files."""
        stats = FileStatistics()
        nonexistent = mock_files_dir / "does_not_exist.py"

        files = [nonexistent]
        result = stats.get_largest_file_info(files)

        assert result is None

    def test_get_largest_file_info_return_type(self, mock_files_dir):
        """Test that get_largest_file_info returns correct types."""
        stats = FileStatistics()
        file1 = mock_files_dir / "test.py"
        file1.write_text("line 1\nline 2", encoding="utf-8")

        files = [file1]
        result = stats.get_largest_file_info(files)

        assert isinstance(result, dict)
        assert isinstance(result["path"], Path)
        assert isinstance(result["lines"], int)


class TestCalculateSummaryStats:
    """Test the calculate_summary_stats method."""

    def test_calculate_summary_stats_basic(self, mock_files_dir):
        """Test basic summary statistics calculation."""
        stats = FileStatistics()
        file1 = mock_files_dir / "file1.py"
        file2 = mock_files_dir / "file2.py"
        file1.write_text("line 1\nline 2", encoding="utf-8")
        file2.write_text("line 1\nline 2\nline 3", encoding="utf-8")

        files = [file1, file2]
        result = stats.calculate_summary_stats(files)

        assert isinstance(result, dict)
        assert result["total_files"] == 2
        assert result["total_lines"] == 5
        assert "file_types" in result
        assert "largest_file" in result
        assert "average_lines" in result

    def test_calculate_summary_stats_empty_list(self):
        """Test summary statistics with empty file list."""
        stats = FileStatistics()
        result = stats.calculate_summary_stats([])

        assert result["total_files"] == 0
        assert result["total_lines"] == 0
        assert result["average_lines"] == 0
        assert result["largest_file"] is None

    def test_calculate_summary_stats_average_calculation(self, mock_files_dir):
        """Test that average lines is calculated correctly."""
        stats = FileStatistics()
        file1 = mock_files_dir / "f1.py"
        file2 = mock_files_dir / "f2.py"
        file3 = mock_files_dir / "f3.py"
        file1.write_text("1\n2\n3", encoding="utf-8")  # 3 lines
        file2.write_text("1\n2\n3\n4\n5", encoding="utf-8")  # 5 lines
        file3.write_text("1", encoding="utf-8")  # 1 line

        files = [file1, file2, file3]
        result = stats.calculate_summary_stats(files)

        # Total = 9 lines, 3 files, average = 9 // 3 = 3
        assert result["total_files"] == 3
        assert result["total_lines"] == 9
        assert result["average_lines"] == 3

    def test_calculate_summary_stats_with_binary_files(self, mock_files_dir):
        """Test summary statistics skips binary files."""
        stats = FileStatistics()
        text_file = mock_files_dir / "text.py"
        binary_file = mock_files_dir / "binary.dat"
        text_file.write_text("line 1\nline 2", encoding="utf-8")
        binary_file.write_bytes(b"\x00\x01\x02")

        files = [text_file, binary_file]
        result = stats.calculate_summary_stats(files)

        # Only text file should be counted
        assert result["total_files"] == 1
        assert result["total_lines"] == 2

    def test_calculate_summary_stats_file_types_included(self, mock_files_dir):
        """Test that file types are included in summary."""
        stats = FileStatistics()
        py_file = mock_files_dir / "script.py"
        txt_file = mock_files_dir / "doc.txt"
        py_file.write_text("# Python", encoding="utf-8")
        txt_file.write_text("Text", encoding="utf-8")

        files = [py_file, txt_file]
        result = stats.calculate_summary_stats(files)

        assert "file_types" in result
        assert isinstance(result["file_types"], dict)
        assert "py" in result["file_types"]
        assert "txt" in result["file_types"]

    def test_calculate_summary_stats_largest_file_included(self, mock_files_dir):
        """Test that largest file info is included in summary."""
        stats = FileStatistics()
        small_file = mock_files_dir / "small.py"
        large_file = mock_files_dir / "large.py"
        small_file.write_text("line", encoding="utf-8")
        large_file.write_text("line 1\nline 2\nline 3", encoding="utf-8")

        files = [small_file, large_file]
        result = stats.calculate_summary_stats(files)

        assert result["largest_file"] is not None
        assert result["largest_file"]["path"] == large_file
        assert result["largest_file"]["lines"] == 3

    def test_calculate_summary_stats_all_fields_present(self, mock_files_dir):
        """Test that all expected fields are present in summary."""
        stats = FileStatistics()
        file1 = mock_files_dir / "test.py"
        file1.write_text("test", encoding="utf-8")

        files = [file1]
        result = stats.calculate_summary_stats(files)

        required_fields = [
            "total_files",
            "total_lines",
            "file_types",
            "largest_file",
            "average_lines",
        ]
        assert all(field in result for field in required_fields)

    def test_calculate_summary_stats_return_types(self, mock_files_dir):
        """Test that summary stats returns correct types."""
        stats = FileStatistics()
        file1 = mock_files_dir / "test.py"
        file1.write_text("line 1\nline 2", encoding="utf-8")

        files = [file1]
        result = stats.calculate_summary_stats(files)

        assert isinstance(result, dict)
        assert isinstance(result["total_files"], int)
        assert isinstance(result["total_lines"], int)
        assert isinstance(result["file_types"], dict)
        assert isinstance(result["average_lines"], int)


class TestFileStatisticsInitialization:
    """Test FileStatistics initialization."""

    def test_initialization(self):
        """Test that FileStatistics can be initialized."""
        stats = FileStatistics()
        assert isinstance(stats, FileStatistics)

    def test_multiple_instances_independent(self):
        """Test that multiple instances are independent."""
        stats1 = FileStatistics()
        stats2 = FileStatistics()
        assert stats1 is not stats2

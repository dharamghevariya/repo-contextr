from contextr.processing.file_reader import (
    format_file_size,
    is_binary_file,
    read_file_content,
)


class TestFormatFileSize:
    """Tests for format_file_size function - simple pure function."""

    # GOOD VALUES: Valid file sizes
    def test_zero_bytes(self):
        """Test formatting 0 bytes."""
        assert format_file_size(0) == "0 B"

    def test_small_bytes(self):
        """Test formatting file sizes under 1KB."""
        assert format_file_size(1) == "1 B"
        assert format_file_size(100) == "100 B"
        assert format_file_size(1023) == "1023 B"

    def test_kilobytes(self):
        """Test formatting file sizes in KB range."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(15360) == "15.0 KB"

    def test_megabytes(self):
        """Test formatting file sizes in MB range."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"
        assert format_file_size(10 * 1024 * 1024) == "10.0 MB"

    def test_fractional_kilobytes(self):
        """Test formatting fractional KB values."""
        result = format_file_size(1536)  # 1.5 KB
        assert "KB" in result
        assert "1.5" in result

    def test_fractional_megabytes(self):
        """Test formatting fractional MB values."""
        result = format_file_size(2 * 1024 * 1024 + 512 * 1024)  # 2.5 MB
        assert "MB" in result
        assert "2.5" in result

    # EDGE CASE: Boundary values
    def test_kb_boundary(self):
        """Test values exactly at KB boundary."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1023) == "1023 B"

    def test_mb_boundary(self):
        """Test values exactly at MB boundary."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 - 1).endswith("KB")


class TestIsBinaryFile:
    """Tests for is_binary_file function - handles file I/O."""

    # GOOD VALUES: Text files
    def test_plain_text_file(self, temp_dir):
        """Test that plain text files are not detected as binary."""
        test_file = temp_dir / "text.txt"
        test_file.write_text("This is plain text content.", encoding="utf-8")

        assert is_binary_file(test_file) is False

    def test_python_source_file(self, temp_dir):
        """Test that Python source files are not binary."""
        test_file = temp_dir / "script.py"
        test_file.write_text("def hello():\n    print('world')\n", encoding="utf-8")

        assert is_binary_file(test_file) is False

    def test_json_file(self, temp_dir):
        """Test that JSON files are not binary."""
        test_file = temp_dir / "data.json"
        test_file.write_text('{"key": "value", "number": 42}', encoding="utf-8")

        assert is_binary_file(test_file) is False

    def test_markdown_file(self, temp_dir):
        """Test that Markdown files are not binary."""
        test_file = temp_dir / "README.md"
        test_file.write_text("# Title\n\nSome content here.", encoding="utf-8")

        assert is_binary_file(test_file) is False

    # BAD VALUES: Binary files
    def test_actual_binary_file(self, temp_dir):
        """Test that binary files are correctly detected."""
        binary_file = temp_dir / "binary.bin"
        # Write actual binary data with non-printable characters
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 100)

        assert is_binary_file(binary_file) is True

    def test_png_image_file(self, temp_dir):
        """Test that PNG images are detected as binary."""
        png_file = temp_dir / "image.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        assert is_binary_file(png_file) is True

    def test_compiled_python_file(self, temp_dir):
        """Test that compiled Python files (.pyc) are binary."""
        pyc_file = temp_dir / "module.pyc"
        # Simplified .pyc header with binary content
        pyc_file.write_bytes(b"\x42\x0d\x0d\x0a" + b"\x00" * 100)

        assert is_binary_file(pyc_file) is True

    # EDGE CASES: Empty and special files
    def test_empty_file_is_not_binary(self, temp_dir):
        """Test that empty files are not considered binary."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        assert is_binary_file(empty_file) is False

    def test_file_with_unicode(self, temp_dir):
        """Test that files with Unicode characters are not binary."""
        unicode_file = temp_dir / "unicode.txt"
        unicode_file.write_text("Hello 🌍\nΓειά σου κόσμε", encoding="utf-8")

        assert is_binary_file(unicode_file) is False

    # ERROR CASES: Nonexistent files
    def test_nonexistent_file_treated_as_binary(self, temp_dir):
        """Test that nonexistent files are treated as binary (error handling)."""
        nonexistent = temp_dir / "does_not_exist.txt"

        # Should not crash, should return True (treat as binary on error)
        assert is_binary_file(nonexistent) is True


class TestReadFileContent:
    """Tests for read_file_content function - complex with multiple code paths."""

    # GOOD VALUES: Normal text files
    def test_read_simple_text_file(self, temp_dir):
        """Test reading a simple text file."""
        test_file = temp_dir / "test.txt"
        content = "Hello, World!\nThis is a test."
        test_file.write_text(content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result == content

    def test_read_python_source_file(self, sample_python_file):
        """Test reading a Python source file with functions and classes."""
        result = read_file_content(sample_python_file)

        assert result is not None
        assert "def add(a, b):" in result
        assert "class Calculator:" in result

    def test_read_multiline_file(self, temp_dir):
        """Test reading files with multiple lines."""
        test_file = temp_dir / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        test_file.write_text(content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result == content
        assert result.count("\n") == 4  # 5 lines = 4 newlines

    # EDGE CASES: Empty files
    def test_read_empty_file(self, temp_dir):
        """Test reading an empty file returns empty string."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        result = read_file_content(test_file)

        assert result == ""

    # GOOD VALUES: Different encodings
    def test_read_utf8_file_with_special_chars(self, temp_dir):
        """Test reading UTF-8 file with special characters."""
        test_file = temp_dir / "utf8.txt"
        content = "Hello 🌍\nΓειά σου κόσμε\n你好世界"
        test_file.write_text(content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result == content

    def test_read_file_with_different_line_endings(self, temp_dir):
        """Test reading files with different line endings (CRLF, LF)."""
        test_file = temp_dir / "mixed_endings.txt"
        # Write with explicit line endings
        test_file.write_bytes(b"Line 1\r\nLine 2\nLine 3\r\n")

        result = read_file_content(test_file)

        assert result is not None
        lines = result.splitlines()
        assert len(lines) >= 3

    # CODE PATH: Large file truncation
    def test_large_file_is_truncated(self, temp_dir):
        """Test that large files (>16KB) are truncated with notice."""
        test_file = temp_dir / "large.txt"
        # Create a file larger than MAX_FILE_SIZE (16KB)
        large_content = "Line of text\n" * 2000  # ~24KB
        test_file.write_text(large_content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result is not None
        assert "File truncated" in result
        assert len(result) < len(large_content)

    def test_truncated_file_has_notice(self, temp_dir):
        """Test that truncated files include truncation notice."""
        test_file = temp_dir / "large.txt"
        large_content = "x" * (20 * 1024)  # 20KB
        test_file.write_text(large_content, encoding="utf-8")

        result = read_file_content(test_file)

        assert "File truncated" in result
        assert "showing first" in result.lower()

    # ERROR CASES: Nonexistent and unreadable files
    def test_nonexistent_file_returns_none(self, temp_dir):
        """Test that reading nonexistent file returns None."""
        nonexistent = temp_dir / "does_not_exist.txt"

        result = read_file_content(nonexistent)

        assert result is None

    # PROPER RETURN TYPE: Verify string or None
    def test_returns_string_or_none(self, temp_dir):
        """Test that function always returns str or None."""
        # Valid file returns string
        valid_file = temp_dir / "valid.txt"
        valid_file.write_text("content")
        result = read_file_content(valid_file)
        assert isinstance(result, str)

        # Invalid file returns None
        invalid_file = temp_dir / "invalid.txt"
        result = read_file_content(invalid_file)
        assert result is None

    def test_returns_correct_content_type(self, temp_dir):
        """Test that returned content is always a string (when successful)."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        result = read_file_content(test_file)

        assert isinstance(result, str)
        assert result == "Test content"

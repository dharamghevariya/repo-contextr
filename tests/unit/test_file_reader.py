"""Unit tests for file reading and processing functionality."""

from contextr.processing.file_reader import (
    format_file_size,
    is_binary_file,
    read_file_content,
)


class TestReadFileContent:
    """Tests for read_file_content function."""

    def test_read_simple_text_file(self, temp_dir):
        """Test reading a simple text file."""
        test_file = temp_dir / "test.txt"
        content = "Hello, World!\nThis is a test."
        test_file.write_text(content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result == content

    def test_read_python_file(self, sample_python_file):
        """Test reading a Python source file."""
        result = read_file_content(sample_python_file)

        assert result is not None
        assert "def add(a, b):" in result
        assert "class Calculator:" in result

    def test_read_empty_file(self, temp_dir):
        """Test reading an empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        result = read_file_content(test_file)

        assert result == ""

    def test_read_utf8_file(self, temp_dir):
        """Test reading a UTF-8 encoded file with special characters."""
        test_file = temp_dir / "utf8.txt"
        content = "Hello 🌍\nΓειά σου κόσμε\n你好世界"
        test_file.write_text(content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result == content

    def test_read_large_file_truncation(self, temp_dir):
        """Test that large files are truncated."""
        test_file = temp_dir / "large.txt"
        # Create a file larger than MAX_FILE_SIZE (16KB)
        large_content = "Line of text\n" * 2000  # ~24KB
        test_file.write_text(large_content, encoding="utf-8")

        result = read_file_content(test_file)

        assert result is not None
        assert "File truncated" in result
        assert len(result) < len(large_content)

    def test_read_nonexistent_file(self, temp_dir):
        """Test reading a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.txt"

        result = read_file_content(nonexistent)

        assert result is None

    def test_read_file_with_different_line_endings(self, temp_dir):
        """Test reading files with different line endings."""
        test_file = temp_dir / "mixed_endings.txt"
        # Write with explicit line endings
        test_file.write_bytes(b"Line 1\r\nLine 2\nLine 3\r\n")

        result = read_file_content(test_file)

        assert result is not None
        lines = result.splitlines()
        assert len(lines) >= 3


class TestIsBinaryFile:
    """Tests for is_binary_file function."""

    def test_text_file_is_not_binary(self, temp_dir):
        """Test that text files are not detected as binary."""
        test_file = temp_dir / "text.txt"
        test_file.write_text("This is plain text content.", encoding="utf-8")

        assert is_binary_file(test_file) is False

    def test_python_file_is_not_binary(self, sample_python_file):
        """Test that Python source files are not binary."""
        assert is_binary_file(sample_python_file) is False

    def test_binary_file_is_detected(self, temp_dir):
        """Test that binary files are correctly detected."""
        binary_file = temp_dir / "binary.bin"
        # Write actual binary data
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 100)

        assert is_binary_file(binary_file) is True

    def test_png_image_is_binary(self, temp_dir):
        """Test that PNG images are detected as binary."""
        png_file = temp_dir / "image.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        assert is_binary_file(png_file) is True

    def test_empty_file_is_not_binary(self, temp_dir):
        """Test that empty files are not considered binary."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        assert is_binary_file(empty_file) is False

    def test_json_file_is_not_binary(self, temp_dir):
        """Test that JSON files are not binary."""
        json_file = temp_dir / "data.json"
        json_file.write_text('{"key": "value", "number": 42}', encoding="utf-8")

        assert is_binary_file(json_file) is False

    def test_markdown_file_is_not_binary(self, temp_dir):
        """Test that Markdown files are not binary."""
        md_file = temp_dir / "README.md"
        md_file.write_text("# Title\n\nSome content here.", encoding="utf-8")

        assert is_binary_file(md_file) is False

    def test_compiled_python_is_binary(self, temp_dir):
        """Test that compiled Python files (.pyc) are binary."""
        pyc_file = temp_dir / "module.pyc"
        # Simplified .pyc header
        pyc_file.write_bytes(b"\x42\x0d\x0d\x0a" + b"\x00" * 100)

        assert is_binary_file(pyc_file) is True


class TestFormatFileSize:
    """Tests for format_file_size function."""

    def test_format_bytes(self):
        """Test formatting sizes in bytes."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(100) == "100 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_kilobytes(self):
        """Test formatting sizes in kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(15360) == "15.0 KB"

    def test_format_megabytes(self):
        """Test formatting sizes in megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"
        assert format_file_size(10 * 1024 * 1024) == "10.0 MB"

    def test_format_fractional_sizes(self):
        """Test formatting fractional sizes."""
        result = format_file_size(1536)  # 1.5 KB
        assert "KB" in result
        assert "1.5" in result

        result = format_file_size(2 * 1024 * 1024 + 512 * 1024)  # 2.5 MB
        assert "MB" in result
        assert "2.5" in result

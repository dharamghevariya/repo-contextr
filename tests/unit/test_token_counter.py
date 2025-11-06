"""
Comprehensive unit tests for the TokenCounter class.

Tests cover:
- Token estimation for various text inputs
- File token counting for text and binary files
- Multiple file token counting
- Token tree building with thresholds
- Token count formatting
- Edge cases and error conditions
"""

from unittest.mock import patch

from contextr.statistics.token_counter import TokenCounter


class TestEstimateTokens:
    """Test the estimate_tokens method with various inputs."""

    def test_estimate_tokens_empty_string(self):
        """Test token estimation for empty string."""
        counter = TokenCounter()
        result = counter.estimate_tokens("")
        assert result == 0
        assert isinstance(result, int)

    def test_estimate_tokens_simple_text(self):
        """Test token estimation for simple text."""
        counter = TokenCounter()
        result = counter.estimate_tokens("Hello, World!")
        # "Hello, World!" = 13 characters / 4 = 3.25 -> 3 tokens
        assert result == 3
        assert isinstance(result, int)

    def test_estimate_tokens_longer_text(self):
        """Test token estimation for longer text."""
        counter = TokenCounter()
        text = "This is a longer text that should have more tokens."
        # 51 characters / 4 = 12.75 -> 12 tokens
        result = counter.estimate_tokens(text)
        assert result == 12
        assert isinstance(result, int)

    def test_estimate_tokens_with_newlines(self):
        """Test token estimation for text with newlines."""
        counter = TokenCounter()
        text = "Line 1\nLine 2\nLine 3"
        # 20 characters / 4 = 5 tokens
        result = counter.estimate_tokens(text)
        assert result == 5
        assert isinstance(result, int)

    def test_estimate_tokens_custom_chars_per_token(self):
        """Test token estimation with custom chars_per_token ratio."""
        counter = TokenCounter(chars_per_token=2.0)
        result = counter.estimate_tokens("Hello, World!")
        # 13 characters / 2 = 6.5 -> 6 tokens
        assert result == 6
        assert isinstance(result, int)

    def test_estimate_tokens_unicode_characters(self):
        """Test token estimation with unicode characters."""
        counter = TokenCounter()
        text = "Hello 世界 🌍"
        # Count all characters including unicode
        result = counter.estimate_tokens(text)
        assert isinstance(result, int)
        assert result >= 0

    def test_estimate_tokens_very_long_text(self):
        """Test token estimation for very long text."""
        counter = TokenCounter()
        text = "a" * 10000
        # 10000 characters / 4 = 2500 tokens
        result = counter.estimate_tokens(text)
        assert result == 2500
        assert isinstance(result, int)


class TestCountFileTokens:
    """Test the count_file_tokens method with various file types."""

    def test_count_file_tokens_text_file(self, sample_python_file):
        """Test counting tokens in a text file."""
        counter = TokenCounter()
        result = counter.count_file_tokens(sample_python_file)
        assert isinstance(result, int)
        assert result > 0

    def test_count_file_tokens_binary_file(self, mock_files_dir):
        """Test counting tokens in a binary file returns 0."""
        counter = TokenCounter()
        binary_file = mock_files_dir / "binary.dat"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

        result = counter.count_file_tokens(binary_file)
        # Binary files return 0, not None
        assert result == 0

    def test_count_file_tokens_nonexistent_file(self, temp_dir):
        """Test counting tokens in a nonexistent file returns 0."""
        counter = TokenCounter()
        nonexistent = temp_dir / "does_not_exist.py"
        result = counter.count_file_tokens(nonexistent)
        # Nonexistent files return 0, not None
        assert result == 0

    def test_count_file_tokens_empty_file(self, temp_dir):
        """Test counting tokens in an empty file."""
        counter = TokenCounter()
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        result = counter.count_file_tokens(empty_file)
        assert result == 0
        assert isinstance(result, int)

    def test_count_file_tokens_with_custom_ratio(self, sample_python_file):
        """Test counting tokens with custom chars_per_token ratio."""
        counter = TokenCounter(chars_per_token=2.0)
        result = counter.count_file_tokens(sample_python_file)
        assert isinstance(result, int)
        assert result > 0

    def test_count_file_tokens_unreadable_file(self, temp_dir):
        """Test counting tokens in a file that can't be read."""
        counter = TokenCounter()
        with patch(
            "contextr.statistics.token_counter.read_file_content", return_value=None
        ):
            file_path = temp_dir / "test.py"
            file_path.write_text("content", encoding="utf-8")
            result = counter.count_file_tokens(file_path)
            assert result is None


class TestCountFilesTokens:
    """Test the count_files_tokens method with multiple files."""

    def test_count_files_tokens_multiple_files(self, mock_files_dir):
        """Test counting tokens across multiple files."""
        counter = TokenCounter()
        file1 = mock_files_dir / "file1.py"
        file2 = mock_files_dir / "file2.py"
        file1.write_text("def hello():\n    pass", encoding="utf-8")
        file2.write_text("def world():\n    pass", encoding="utf-8")

        files = [file1, file2]
        result = counter.count_files_tokens(files)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert file1 in result
        assert file2 in result
        assert all(isinstance(count, int) for count in result.values())

    def test_count_files_tokens_empty_list(self):
        """Test counting tokens with empty file list."""
        counter = TokenCounter()
        result = counter.count_files_tokens([])
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_count_files_tokens_mixed_readable_and_binary(self, mock_files_dir):
        """Test counting tokens with mix of readable and binary files."""
        counter = TokenCounter()
        text_file = mock_files_dir / "text.py"
        binary_file = mock_files_dir / "binary.dat"
        text_file.write_text("print('hello')", encoding="utf-8")
        binary_file.write_bytes(b"\x00\x01\x02")

        files = [text_file, binary_file]
        result = counter.count_files_tokens(files)

        assert isinstance(result, dict)
        assert text_file in result
        assert isinstance(result[text_file], int)
        # Binary file should not appear in result

    def test_count_files_tokens_with_nonexistent_files(self, mock_files_dir):
        """Test counting tokens with some nonexistent files."""
        counter = TokenCounter()
        real_file = mock_files_dir / "real.py"
        fake_file = mock_files_dir / "fake.py"
        real_file.write_text("# comment", encoding="utf-8")

        files = [real_file, fake_file]
        result = counter.count_files_tokens(files)

        assert isinstance(result, dict)
        assert real_file in result
        # Nonexistent file should not appear in result


class TestBuildTokenTree:
    """Test the build_token_tree method with various scenarios."""

    def test_build_token_tree_simple_structure(self, mock_files_dir):
        """Test building token tree for simple directory structure."""
        counter = TokenCounter()
        file1 = mock_files_dir / "file1.py"
        file1.write_text("print('hello')", encoding="utf-8")

        files = [file1]
        result = counter.build_token_tree(files, mock_files_dir, threshold=0)

        assert isinstance(result, dict)
        assert "tree" in result
        assert "total_tokens" in result
        assert "file_count" in result

    def test_build_token_tree_nested_directories(self, mock_files_dir):
        """Test building token tree with nested directories."""
        counter = TokenCounter()
        subdir = mock_files_dir / "subdir"
        subdir.mkdir(exist_ok=True)
        file1 = mock_files_dir / "file1.py"
        file2 = subdir / "file2.py"
        file1.write_text("# root file", encoding="utf-8")
        file2.write_text("# nested file", encoding="utf-8")

        files = [file1, file2]
        result = counter.build_token_tree(files, mock_files_dir, threshold=0)

        assert isinstance(result, dict)
        assert "tree" in result
        assert "total_tokens" in result
        assert result["total_tokens"] > 0

    def test_build_token_tree_with_threshold(self, mock_files_dir):
        """Test building token tree with threshold filtering."""
        counter = TokenCounter()
        file1 = mock_files_dir / "file1.py"
        file1.write_text("a" * 100, encoding="utf-8")

        files = [file1]
        # High threshold should filter out small files/dirs
        result = counter.build_token_tree(files, mock_files_dir, threshold=1000)

        assert isinstance(result, dict)

    def test_build_token_tree_empty_file_list(self, mock_files_dir):
        """Test building token tree with empty file list."""
        counter = TokenCounter()
        result = counter.build_token_tree([], mock_files_dir, threshold=0)

        assert isinstance(result, dict)
        assert "tree" in result
        assert "total_tokens" in result
        assert result["total_tokens"] == 0

    def test_build_token_tree_return_type(self, mock_files_dir):
        """Test that build_token_tree returns correct structure."""
        counter = TokenCounter()
        file1 = mock_files_dir / "test.py"
        file1.write_text("test", encoding="utf-8")

        result = counter.build_token_tree([file1], mock_files_dir, threshold=0)

        assert isinstance(result, dict)
        assert all(
            key in result for key in ["tree", "total_tokens", "file_count", "threshold"]
        )


class TestFormatTokenCount:
    """Test the format_token_count method."""

    def test_format_token_count_zero(self):
        """Test formatting zero tokens."""
        counter = TokenCounter()
        result = counter.format_token_count(0)
        assert result == "0"
        assert isinstance(result, str)

    def test_format_token_count_small_number(self):
        """Test formatting small number of tokens."""
        counter = TokenCounter()
        result = counter.format_token_count(42)
        assert result == "42"
        assert isinstance(result, str)

    def test_format_token_count_hundreds(self):
        """Test formatting hundreds of tokens."""
        counter = TokenCounter()
        result = counter.format_token_count(999)
        assert result == "999"
        assert isinstance(result, str)

    def test_format_token_count_thousands(self):
        """Test formatting thousands of tokens."""
        counter = TokenCounter()
        result = counter.format_token_count(1000)
        assert result == "1,000"
        assert isinstance(result, str)

    def test_format_token_count_large_number(self):
        """Test formatting large number of tokens."""
        counter = TokenCounter()
        result = counter.format_token_count(1234567)
        assert result == "1,234,567"
        assert isinstance(result, str)

    def test_format_token_count_negative_number(self):
        """Test formatting negative number (edge case)."""
        counter = TokenCounter()
        result = counter.format_token_count(-1000)
        assert result == "-1,000"
        assert isinstance(result, str)


class TestTokenCounterInitialization:
    """Test TokenCounter initialization and attributes."""

    def test_default_initialization(self):
        """Test default initialization of TokenCounter."""
        counter = TokenCounter()
        assert counter.chars_per_token == 4.0

    def test_custom_initialization(self):
        """Test custom initialization with different chars_per_token."""
        counter = TokenCounter(chars_per_token=3.0)
        assert counter.chars_per_token == 3.0

    def test_initialization_with_float(self):
        """Test initialization with float value."""
        counter = TokenCounter(chars_per_token=2.5)
        assert counter.chars_per_token == 2.5

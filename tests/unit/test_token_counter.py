"""Unit tests for token counting functionality."""

import pytest

from contextr.statistics.token_counter import CHARS_PER_TOKEN, TokenCounter


class TestTokenCounter:
    """Tests for TokenCounter class."""

    @pytest.fixture
    def token_counter(self):
        """Create a TokenCounter instance."""
        return TokenCounter()

    def test_estimate_tokens_empty_string(self, token_counter):
        """Test token estimation for empty string."""
        result = token_counter.estimate_tokens("")

        assert result == 0

    def test_estimate_tokens_simple_text(self, token_counter):
        """Test token estimation for simple text."""
        text = "Hello, World!"  # 13 characters
        result = token_counter.estimate_tokens(text)

        # ~4 chars per token, so 13/4 = 3.25 -> 3 tokens
        assert result == 3

    def test_estimate_tokens_longer_text(self, token_counter):
        """Test token estimation for longer text."""
        text = "This is a longer piece of text for testing."  # 43 chars
        result = token_counter.estimate_tokens(text)

        # 43/4 = 10.75 -> 10 tokens (integer division)
        assert result == 10

    def test_estimate_tokens_with_newlines(self, token_counter):
        """Test that newlines are counted in token estimation."""
        text = "Line 1\nLine 2\nLine 3"  # 20 characters including newlines
        result = token_counter.estimate_tokens(text)

        # 20/4 = 5 tokens
        assert result == 5

    def test_estimate_tokens_custom_ratio(self):
        """Test token estimation with custom chars per token ratio."""
        counter = TokenCounter(chars_per_token=2.0)
        text = "Hello"  # 5 characters

        result = counter.estimate_tokens(text)

        # 5/2 = 2.5 -> 2 tokens
        assert result == 2

    def test_count_file_tokens(self, token_counter, temp_dir):
        """Test counting tokens in a file."""
        test_file = temp_dir / "test.py"
        content = "def hello():\n    print('hello')\n"  # 32 chars
        test_file.write_text(content)

        result = token_counter.count_file_tokens(test_file)

        assert result is not None
        # 32/4 = 8 tokens
        assert result == 8

    def test_count_file_tokens_empty_file(self, token_counter, temp_dir):
        """Test counting tokens in an empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")

        result = token_counter.count_file_tokens(test_file)

        assert result == 0

    def test_count_file_tokens_binary_file(self, token_counter, temp_dir):
        """Test that binary files return 0 tokens."""
        binary_file = temp_dir / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        result = token_counter.count_file_tokens(binary_file)

        assert result == 0

    def test_count_file_tokens_nonexistent_file(self, token_counter, temp_dir):
        """Test counting tokens for nonexistent file."""
        nonexistent = temp_dir / "nonexistent.txt"

        result = token_counter.count_file_tokens(nonexistent)

        # Nonexistent files are treated as binary (exception handling), so return 0
        assert result == 0

    def test_count_files_tokens(self, token_counter, temp_dir):
        """Test counting tokens for multiple files."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("Hello World")  # 11 chars = 2 tokens
        file2.write_text("Test content here")  # 17 chars = 4 tokens

        files = [file1, file2]
        result = token_counter.count_files_tokens(files)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert file1 in result
        assert file2 in result
        assert result[file1] == 2
        assert result[file2] == 4

    def test_count_files_tokens_skips_unreadable(self, token_counter, temp_dir):
        """Test that unreadable files are handled."""
        file1 = temp_dir / "readable.txt"
        file2 = temp_dir / "nonexistent.txt"
        file1.write_text("content")

        files = [file1, file2]
        result = token_counter.count_files_tokens(files)

        # Both files get a result - readable has count, nonexistent has 0
        assert len(result) == 2
        assert file1 in result
        assert result[file1] > 0
        assert file2 in result
        assert result[file2] == 0  # Nonexistent treated as binary

    def test_build_token_tree(self, token_counter, temp_dir):
        """Test building a token tree structure."""
        # Create file structure
        (temp_dir / "file1.py").write_text("x" * 40)  # 10 tokens
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.py").write_text("x" * 20)  # 5 tokens

        files = [temp_dir / "file1.py", subdir / "file2.py"]

        result = token_counter.build_token_tree(files, temp_dir)

        assert "tree" in result
        assert "total_tokens" in result
        assert "file_count" in result
        assert result["total_tokens"] == 15  # 10 + 5
        assert result["file_count"] == 2

    def test_build_token_tree_with_threshold(self, token_counter, temp_dir):
        """Test building token tree with threshold filtering."""
        (temp_dir / "large.py").write_text("x" * 100)  # 25 tokens
        (temp_dir / "small.py").write_text("x" * 8)  # 2 tokens

        files = list(temp_dir.rglob("*.py"))

        result = token_counter.build_token_tree(files, temp_dir, threshold=10)

        # Should only include the large file
        assert result["file_count"] == 1
        assert result["total_tokens"] == 25

    def test_build_token_tree_empty_files(self, token_counter, temp_dir):
        """Test building token tree with no files."""
        result = token_counter.build_token_tree([], temp_dir)

        assert result["total_tokens"] == 0
        assert result["file_count"] == 0
        assert result["tree"] == {}

    def test_build_token_tree_nested_directories(self, token_counter, temp_dir):
        """Test token tree with nested directory structure."""
        # Create nested structure
        src = temp_dir / "src"
        src.mkdir()
        utils = src / "utils"
        utils.mkdir()

        (src / "main.py").write_text("x" * 40)  # 10 tokens
        (utils / "helper.py").write_text("x" * 20)  # 5 tokens

        files = list(temp_dir.rglob("*.py"))

        result = token_counter.build_token_tree(files, temp_dir)

        assert result["total_tokens"] == 15
        assert "src" in result["tree"]

    def test_calculate_directory_totals(self, token_counter):
        """Test that directory totals are calculated correctly."""
        tree = {
            "src": {
                "_type": "directory",
                "_tokens": 0,
                "_children": {
                    "file1.py": {"_type": "file", "_tokens": 10},
                    "file2.py": {"_type": "file", "_tokens": 5},
                },
            }
        }

        token_counter._calculate_directory_totals(tree)

        # Directory should have sum of its children
        assert tree["src"]["_tokens"] == 15

    def test_format_token_count(self, token_counter):
        """Test formatting token counts with thousands separator."""
        assert token_counter.format_token_count(0) == "0"
        assert token_counter.format_token_count(100) == "100"
        assert token_counter.format_token_count(1000) == "1,000"
        assert token_counter.format_token_count(1234) == "1,234"
        assert token_counter.format_token_count(1234567) == "1,234,567"

    def test_format_token_count_large_numbers(self, token_counter):
        """Test formatting large token counts."""
        result = token_counter.format_token_count(1000000)
        assert result == "1,000,000"

        result = token_counter.format_token_count(123456789)
        assert result == "123,456,789"


class TestTokenCounterConstants:
    """Tests for token counter constants."""

    def test_chars_per_token_constant(self):
        """Test that the CHARS_PER_TOKEN constant is set correctly."""
        assert CHARS_PER_TOKEN == 4.0

    def test_default_chars_per_token(self):
        """Test that TokenCounter uses the correct default."""
        counter = TokenCounter()
        assert counter.chars_per_token == CHARS_PER_TOKEN

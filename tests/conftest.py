import os
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_git_repo(temp_dir):
    """Create a sample git repository for testing."""
    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    # Create sample files
    (temp_dir / "README.md").write_text("# Test Repository\n\nThis is a test.")
    (temp_dir / "main.py").write_text('print("Hello, World!")\n')
    (temp_dir / "utils.py").write_text('def helper():\n    return "help"\n')

    # Create a subdirectory with files
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text('def main():\n    print("app")\n')

    # Add and commit
    subprocess.run(
        ["git", "add", "."],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )

    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test User",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test User",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )

    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
        env=env,
    )

    return temp_dir


@pytest.fixture
def non_git_dir(temp_dir):
    """Create a directory that is not a git repository."""
    (temp_dir / "file.txt").write_text("Not a git repo")
    return temp_dir


@pytest.fixture
def mock_files_dir(temp_dir):
    """Create a directory with various file types for testing."""
    # Python files
    (temp_dir / "app.py").write_text("# Python code\nprint('hello')\n")
    (temp_dir / "utils.py").write_text('def util():\n    return "data"\n')

    # JavaScript files
    (temp_dir / "script.js").write_text("// JavaScript code\nconsole.log('hello');\n")

    # Markdown files
    (temp_dir / "README.md").write_text("# Title\n\nContent here.\n")
    (temp_dir / "NOTES.md").write_text("## Notes\n\n- Item 1\n- Item 2\n")

    # Binary file
    (temp_dir / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    # Large file (>16KB)
    large_content = "Line of text\n" * 2000  # ~24KB
    (temp_dir / "large.txt").write_text(large_content)

    # Create subdirectories
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.py").write_text("# Nested file\n")

    # Create excluded directories
    excluded = temp_dir / "__pycache__"
    excluded.mkdir()
    (excluded / "cache.pyc").write_bytes(b"compiled")

    node_modules = temp_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.json").write_text('{"name": "test"}')

    return temp_dir


@pytest.fixture
def empty_dir(temp_dir):
    """Create an empty directory."""
    return temp_dir


@pytest.fixture
def recent_files_repo(sample_git_repo):
    """Create a git repo with recent and old files."""
    import time

    # The sample_git_repo already has files
    # Add a new file and commit (will be recent)
    time.sleep(1)  # Ensure different timestamp

    new_file = sample_git_repo / "new_file.py"
    new_file.write_text('def new_func():\n    return "new"\n')

    subprocess.run(
        ["git", "add", "new_file.py"],
        cwd=sample_git_repo,
        check=True,
        capture_output=True,
    )

    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test User",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test User",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        }
    )

    subprocess.run(
        ["git", "commit", "-m", "Add new file"],
        cwd=sample_git_repo,
        check=True,
        capture_output=True,
        env=env,
    )

    return sample_git_repo


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file."""
    file_path = temp_dir / "sample.py"
    content = '''"""Sample Python module."""


def add(a, b):
    """Add two numbers."""
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.result = 0

    def calculate(self, a, b, operation):
        """Perform a calculation."""
        if operation == "add":
            return add(a, b)
        elif operation == "multiply":
            return multiply(a, b)
        return 0
'''
    file_path.write_text(content)
    return file_path

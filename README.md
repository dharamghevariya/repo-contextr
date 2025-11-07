# repo-contextr

[![PyPI version](https://badge.fury.io/py/repo-contextr.svg)](https://badge.fury.io/py/repo-contextr)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributing](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful Repository Context Packager CLI tool that analyzes local git repositories and creates comprehensive text files containing repository content optimized for sharing with Large Language Models (LLMs).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment with uv
- Running tests and code quality checks
- Submitting pull requests
- Code style guidelines
- Project structure and development workflow

## Quick Start

```bash
# Install from PyPI
pip install repo-contextr

# Or use pipx (recommended for CLI tools)
pipx install repo-contextr

# Package your current repository
repo-contextr .

# Save to file
repo-contextr . -o my-project-context.txt
```

## Overview

When developers want to get help from ChatGPT, Claude, or other LLMs about their code, they often struggle with how to share their codebase effectively. **repo-contextr** solves this by automatically collecting and formatting repository content into a single, well-structured text file that provides rich context to LLMs, enabling them to give much better assistance with your code.

## Features

- **Git Integration**: Extracts commit SHA, branch, author, and date information
- **Project Structure**: Generates a clear directory tree visualization
- **Token Counting**: Estimate and visualize token distribution across your codebase (NEW!)
- **File Content Packaging**: Includes file contents with syntax highlighting
- **Smart File Discovery**: Recursively scans directories with configurable filtering
- **Binary File Detection**: Automatically skips binary files
- **Recent Changes Mode**: Focus on files modified in the last 7 days with git timestamps
- **File Type Statistics**: Shows breakdown of file types with counts (e.g., .py (8), .md (3))
- **Size Analytics**: Displays largest file and average file size information
- **Git Timestamps**: Shows last modified dates for files using git history
- **Pattern Matching**: Include/exclude files using glob patterns
- **Error Handling**: Gracefully handles permission errors and provides helpful messages
- **Flexible Output**: Write to stdout or save to a file

## Installation

### From PyPI (Recommended)

```bash
# Install globally with pipx (recommended)
pipx install repo-contextr

# Or install with pip
pip install repo-contextr

# Verify installation
repo-contextr --version
```

### From Source

```bash
# Clone the repository
git clone https://github.com/dharamghevariya/repo-contextr.git
cd repo-contextr

# Install in development mode
pip install -e .
```

## Usage

### Basic Commands

```bash
# Package current directory
repo-contextr .

# Package specific directory
repo-contextr /path/to/your/project

# Package specific files
repo-contextr src/main.py src/utils.py

# Save output to file
repo-contextr . -o my-project-context.txt

# Include only Python files
repo-contextr . --include "*.py"

# Include only recent changes (last 7 days)
repo-contextr . --recent

# Combine filters
repo-contextr . --recent --include "*.py" -o recent-python.txt

# Show token counts in structure and summary
repo-contextr . --token-count-tree -o context-with-tokens.txt

# Filter tree to show only high-token files
repo-contextr . --token-count-tree --token-threshold 1000

# Just get total token count
repo-contextr . --tokens
```

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `paths` | - | File or directory paths to analyze | `repo-contextr src/ docs/` |
| `--output` | `-o` | Output file path (default: stdout) | `-o context.txt` |
| `--include` | - | Pattern to include files (glob pattern) | `--include "*.py"` |
| `--recent` | `-r` | Only files modified in last 7 days | `--recent` |
| `--token-count-tree` | - | Show token counts in structure | `--token-count-tree` |
| `--token-threshold` | - | Minimum token count to include | `--token-threshold 1000` |
| `--tokens` | - | Show estimated total token count | `--tokens` |
| `--version` | `-v` | Show version and exit | `-v` |
| `--help` | `-h` | Show help message | `-h` |

### Real-World Examples

```bash
# Get help with a Python project
repo-contextr . --include "*.py" -o python-context.txt

# Share recent changes for code review
repo-contextr . --recent -o recent-changes.txt

# Package documentation files
repo-contextr . --include "*.md" -o docs-context.txt

# Full project context for LLM assistance
repo-contextr . -o full-project.txt

# Focus on backend code only
repo-contextr backend/ --include "*.{py,sql,yaml}" -o backend-context.txt

# Estimate token usage for LLM context planning
repo-contextr . --tokens

# Identify token-heavy files for optimization
repo-contextr . --token-count-tree --token-threshold 500 -o high-token-files.txt
```

## Output Format

The tool generates a structured text file with the following sections:

### 1. File System Location
Absolute path to the repository being analyzed

### 2. Git Information
- Commit SHA
- Current branch
- Last commit author
- Last commit date

### 3. Project Structure
Directory tree showing the organization of included files

**With Token Counting** (when using `--token-count-tree` or `--tokens`):
- Shows token estimates for each file and directory
- Displays total tokens for the entire project
- Helps identify token-heavy files and directories
- Supports filtering with `--token-threshold` to focus on high-token files

Example with tokens:
```
## Structure

**Total Tokens:** 11,738
contextr/ (11,738 tokens)
├── commands/ (1,416 tokens)
│   ├── package.py (726 tokens)
│   └── token_commands.py (690 tokens)
├── formatters/ (3,542 tokens)
│   ├── report_formatter.py (2,157 tokens)
│   └── token_tree_formatter.py (1,385 tokens)
└── cli.py (1,068 tokens)
```

### 4. File Contents
Each file's content with:
- Clear file path headers with git timestamps (when available)
- Appropriate syntax highlighting language tags
- Truncation notices for large files

### 5. Recent Changes (when --recent is used)
- Shows only files modified in the last 7 days with git timestamps
- Includes file contents and statistics for those files
- Adds a summary line indicating how many recent files were found

### 6. Summary Statistics
- Total number of files processed
- Total lines of code
- Recent files count (last 7 days)
- **Estimated tokens** (when token counting is enabled)
- File type breakdown with counts
- Largest file with line count
- Average file size in lines

## Token Counting for LLM Context Optimization

**repo-contextr** includes built-in token estimation to help you optimize content for LLM context windows. This feature uses the industry-standard approximation of ~4 characters per token.

### Why Token Counting Matters

When working with LLMs like ChatGPT, Claude, or other AI assistants, you're limited by context windows (e.g., 8K, 32K, 128K tokens). Understanding your repository's token distribution helps you:

- **Stay within context limits**: Know if your repo fits in the LLM's context window
- **Optimize file selection**: Identify which files consume the most tokens
- **Manage API costs**: Estimate token usage for cost planning
- **Make strategic decisions**: Decide what to include, summarize, or exclude

### Token Counting Options

#### 1. Quick Token Count
Get just the total estimated tokens:
```bash
repo-contextr . --tokens
# Output: Estimated tokens: 24,515 (across 40 files)
```

#### 2. Token Distribution Tree
See token counts for each file and directory in the structure:
```bash
repo-contextr . --token-count-tree -o context.txt
```

This adds token annotations to your regular repository output:
```
## Structure

**Total Tokens:** 11,738

src/ (11,738 tokens)
├── core/ (7,402 tokens)
│   ├── engine.py (4,250 tokens)
│   └── utils.py (3,152 tokens)
└── tests/ (4,336 tokens)
    └── test_engine.py (4,336 tokens)
```

#### 3. Filter by Token Threshold
Focus on token-heavy files only:
```bash
repo-contextr . --token-count-tree --token-threshold 1000
```

This shows only files and directories with ≥1000 tokens, helping you identify optimization targets.

### Use Cases for Token Counting

- **Context Planning**: Determine if your project fits in GPT-4's 128K context
- **File Prioritization**: Identify which files to include for maximum value
- **Cost Estimation**: Estimate API costs before processing
- **Optimization**: Find files that could be summarized or split
- **Debugging**: Understand why you're hitting context limits

### Token Estimation Accuracy

The tool uses **~4 characters per token**, which is accurate for:
- English code and comments
- Common programming languages (Python, JavaScript, Java, etc.)
- Documentation in English

May be less accurate for:
- Non-English text
- Heavily compressed/minified code
- Special characters and unicode

## Example Output

When you run `repo-contextr . --include "*.py"`, the output looks like this:

````markdown
# Repository Context

## File System Location

/home/user/my-project

## Git Info

- Commit: a1b2c3d4e5f6789...
- Branch: main
- Author: John Doe <john@example.com>
- Date: Wed Sep 25 14:30:15 2025 -0400

## Structure

```
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── pyproject.toml
└── README.md
```

## Recent Changes

### File: src/main.py (Modified: 2025-09-25 14:30:22)
```python
#!/usr/bin/env python3
"""Main entry point for the application."""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

## File Contents

### File: src/utils/helpers.py (Modified: 2025-09-24 10:15:33)
```python
"""Utility functions for the application."""

def format_output(data):
    """Format data for display."""
    return str(data)
```

## Summary
- Total files: 2
- Total lines: 12
- Recent files (last 7 days): 1
- Estimated tokens: 3,142
- File types: .py (2)
- Largest file: src/utils/helpers.py (8 lines)
- Average file size: 6 lines
````

## What Files Are Included

The tool includes most text files but automatically excludes:

### Excluded Directories
- `.git`, `.svn`, `.hg` (version control)
- `__pycache__`, `.pytest_cache` (Python cache)
- `node_modules`, `.npm` (Node.js)
- `.vscode`, `.idea` (IDE directories)
- `build`, `dist`, `target` (build directories)
- `.env`, `venv`, `.venv` (virtual environments)

### File Handling Rules
- **Binary files**: Automatically detected and skipped
- **Large files**: Files larger than 16KB are truncated with notice
- **Permission errors**: Skipped with warning message to stderr
- **Text files**: All readable text files are included by default

### Pattern Matching
Use the `--include` option to filter files:
```bash
repo-contextr . --include "*.py"           # Only Python files
repo-contextr . --include "*.{js,ts}"      # JavaScript and TypeScript
repo-contextr . --include "*.md"           # Only Markdown files
repo-contextr . --include "src/**/*.py"    # Python files in src/
```

## Error Handling

The tool handles errors gracefully:

| Error Type | Behavior | Example |
|------------|----------|---------|
| **Permission errors** | Skipped with warning | `Warning: Permission denied: /restricted/file.txt` |
| **Binary files** | Automatically skipped | `.exe`, `.jpg`, `.pdf` files ignored |
| **Large files** | Truncated with notice | `[File truncated - original size: 25KB]` |
| **Invalid paths** | Clear error messages | `Error: Path does not exist: /invalid/path` |
| **Non-git repositories** | Works fine | Shows "Not a git repository" in output |
| **Network issues** | Graceful fallback | Git info shows as unavailable |

## Development

### Testing

This project uses [pytest](https://docs.pytest.org/) for comprehensive testing with full coverage reporting and detailed code coverage analysis.

**Quick Start:**
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Generate interactive HTML coverage report
uv run pytest --cov=src --cov-report=html
start htmlcov/index.html
```

**Advanced Testing Features:**

#### 1. Running Individual Tests
Run specific tests instead of the entire suite:
```bash
# Run a single test function
uv run pytest tests/unit/test_token_counter.py::TestEstimateTokens::test_estimate_tokens_empty_string -v

# Run all tests in a class
uv run pytest tests/unit/test_token_counter.py::TestEstimateTokens -v

# Run specific test file
uv run pytest tests/unit/test_token_counter.py -v

# Run tests matching a pattern
uv run pytest -k "token" -v
```

#### 2. Code Coverage Analysis
Track which code is tested and identify missing test cases:
```bash
# Coverage with missing lines highlighted
uv run pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report (interactive, visual)
uv run pytest --cov=src --cov-report=html
start htmlcov/index.html

# Coverage for specific module
uv run pytest tests/unit/test_token_counter.py --cov=src.contextr.statistics.token_counter --cov-report=term-missing
```

**Coverage Status:**
- **file_reader.py**: 96% coverage
- **file_stats.py**: 94% coverage
- **token_counter.py**: 95% coverage
- **Core modules**: 93%+ coverage
- **Total**: 104 comprehensive tests

**Understanding Coverage Reports:**
- **Terminal Report**: Shows percentage and missing line numbers
- **HTML Report**: Interactive, color-coded line-by-line view
  - 🟢 Green = Covered by tests
  - 🔴 Red = Not covered (write tests for these!)
  - ⚪ Gray = Non-executable (comments, blank lines)

#### 3. Debugging Tests
```bash
# Show print statements in tests
uv run pytest -s tests/unit/test_token_counter.py

# Stop on first failure
uv run pytest -x

# Run only failed tests from last run
uv run pytest --lf

# Very verbose output
uv run pytest -vv
```

**Testing Documentation:**
- **[TESTING.md](TESTING.md)** - Comprehensive testing guide
- **[COVERAGE.md](COVERAGE.md)** - Code coverage guide

**Test Structure:**
```
tests/
├── conftest.py              # Shared fixtures (git repos, temp dirs, mock files)
├── test_smoke.py            # Basic smoke tests
├── unit/                    # Unit tests for individual modules
│   ├── test_config.py       # Configuration and TOML tests
│   ├── test_file_reader.py  # File reading and processing tests
│   ├── test_file_stats.py   # File statistics tests
│   └── test_token_counter.py # Token counting tests
├── integration/             # End-to-end workflow tests
└── fixtures/                # Test data and samples
```

**Available Fixtures:**
- `temp_dir` - Temporary directory for isolated tests
- `sample_git_repo` - Initialized git repository with sample files
- `non_git_dir` - Non-git directory for testing fallback behavior
- `mock_files_dir` - Directory with various file types (Python, JS, MD, binary)
- `empty_dir` - Empty directory
- `recent_files_repo` - Git repo with recent commits for timestamp testing
- `sample_python_file` - Sample Python file with functions and classes

**Continuous Integration:**
Tests run automatically on push/PR via GitHub Actions on Ubuntu, Windows, and macOS.

### Code Formatting and Linting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both code formatting and linting, which provides fast and comprehensive code quality checks.

**Running the formatter manually:**
```bash
uv run ruff format .
```

**Running the linter:**
```bash
uv run ruff check .
```

**Auto-fix linting issues:**
```bash
uv run ruff check --fix .
```

**Pre-commit hooks:**
The project uses pre-commit hooks that automatically format and check your code before each commit. To install the hooks:
```bash
uv run pre-commit install
```

Once installed, Ruff will automatically format your code and run linting checks whenever you commit changes.

**Running all checks (like CI does):**
```bash
# Linting
uv run ruff check .
uv run ruff format --check .

# Type checking
uv run mypy src

# Tests with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Use Cases

Perfect for these scenarios:

- **AI Assistance**: Get better help from ChatGPT, Claude, or GitHub Copilot
- **LLM Context Optimization**: Estimate and manage token usage to stay within context limits
- **Code Reviews**: Share complete project context with team members
- **Documentation**: Create comprehensive project snapshots
- **Onboarding**: Help new team members understand project structure
- **Debugging**: Share complete context when asking for help
- **Learning**: Analyze and understand other projects' structure
- **Cost Management**: Estimate API costs for LLM processing before submission

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Links

- **PyPI Package**: https://pypi.org/project/repo-contextr/
- **GitHub Repository**: https://github.com/dharamghevariya/repo-contextr
- **Issue Tracker**: https://github.com/dharamghevariya/repo-contextr/issues
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation**: This README

---

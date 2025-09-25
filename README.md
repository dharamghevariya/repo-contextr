# repo-contextr

[![PyPI version](https://badge.fury.io/py/repo-contextr.svg)](https://badge.fury.io/py/repo-contextr)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/repo-contextr)](https://pepy.tech/project/repo-contextr)

A powerful Repository Context Packager CLI tool that analyzes local git repositories and creates comprehensive text files containing repository content optimized for sharing with Large Language Models (LLMs).

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
- **File Content Packaging**: Includes file contents with syntax highlighting
- **Smart File Discovery**: Recursively scans directories with configurable filtering
- **Binary File Detection**: Automatically skips binary files
- **Recent Changes Mode**: Focus on files modified in the last 7 days
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
```

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `paths` | - | File or directory paths to analyze | `repo-contextr src/ docs/` |
| `--output` | `-o` | Output file path (default: stdout) | `-o context.txt` |
| `--include` | - | Pattern to include files (glob pattern) | `--include "*.py"` |
| `--recent` | `-r` | Only files modified in last 7 days | `--recent` |
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

### 4. File Contents
Each file's content with:
- Clear file path headers
- Appropriate syntax highlighting language tags
- Truncation notices for large files

### 5. Recent Changes (when --recent is used)
- Shows only files modified in the last 7 days
- Includes file contents and statistics for those files
- Adds a summary line indicating how many recent files were found

### 6. Summary Statistics
- Total number of files processed
- Total lines of code
- Recent files count

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

### File: src/main.py
```python
#!/usr/bin/env python3
"""Main entry point for the application."""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

## File Contents

### File: src/utils/helpers.py
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

## Contributing

We welcome contributions! Here's how to get started:

### Quick Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/yourusername/repo-contextr.git
cd repo-contextr

# 3. Install in development mode
pip install -e .

# 4. Make your changes and test
repo-contextr . --include "*.py"

# 5. Submit a pull request
```

### Development Workflow

```bash
# Setup development environment  
git clone https://github.com/dharamghevariya/repo-contextr.git
cd repo-contextr
pip install -e ".[dev]"

# Make changes to src/contextr/

# Test your changes
repo-contextr . -o test-output.txt

# Run tests (when available)
pytest

# Format code
black src/

# Check types
mypy src/
```

### Project Structure

```
repo-contextr/
├── src/
│   └── contextr/
│       ├── __init__.py       # Package initialization
│       ├── cli.py           # CLI interface using Typer
│       ├── commands/
│       │   ├── __init__.py
│       │   └── package.py   # Main packaging logic
│       └── utils/
│           ├── __init__.py
│           └── helpers.py   # Utility functions
├── pyproject.toml           # Project configuration
├── README.md               # This documentation
├── LICENSE                 # MIT License
└── tests/                  # Test files (coming soon)
```

## Use Cases

Perfect for these scenarios:

- **AI Assistance**: Get better help from ChatGPT, Claude, or GitHub Copilot
- **Code Reviews**: Share complete project context with team members  
- **Documentation**: Create comprehensive project snapshots
- **Onboarding**: Help new team members understand project structure
- **Debugging**: Share complete context when asking for help
- **Learning**: Analyze and understand other projects' structure

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Links

- **PyPI Package**: https://pypi.org/project/repo-contextr/
- **GitHub Repository**: https://github.com/dharamghevariya/repo-contextr
- **Issue Tracker**: https://github.com/dharamghevariya/repo-contextr/issues
- **Documentation**: This README

---

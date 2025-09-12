# contextr

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Repository Context Packager CLI tool that analyzes local git repositories and creates comprehensive text files containing repository content optimized for sharing with Large Language Models (LLMs).

## 🎯 Overview

When developers want to get help from ChatGPT, Claude, or other LLMs about their code, they often struggle with how to share their codebase effectively. Common problems include:

- **Lost Context**: Copy-pasting individual files loses important project structure and relationships
- **Missing Dependencies**: LLMs can't see how files connect or what libraries are used
- **Incomplete Picture**: Hard to convey the overall architecture and organization
- **Manual Work**: Time-consuming to gather and format relevant code

**contextr** solves this by automatically collecting and formatting repository content into a single, well-structured text file that provides rich context to LLMs, enabling them to give much better assistance with your code.

## ✨ Features

- **🔗 Git Integration**: Extracts commit SHA, branch, author, and date information
- **🌳 Project Structure**: Generates a clear directory tree visualization
- **📦 File Content Packaging**: Includes file contents with syntax highlighting
- **🔍 Smart File Discovery**: Recursively scans directories with configurable filtering
- **📏 Large File Handling**: Truncates files larger than 16KB with clear notices
- **🚫 Binary File Detection**: Automatically skips binary files
- **⚠️ Error Handling**: Gracefully handles permission errors and provides helpful messages
- **💾 Flexible Output**: Write to stdout or save to a file
- **🎯 Pattern Matching**: Include/exclude files using glob patterns

## Installation

### Prerequisites

- Python 3.12 or higher
- Git (for git repository analysis)
- [pipx](https://pypa.github.io/pipx/) (recommended for global installation)

### For End Users

```bash
# Install pipx if you don't have it
pip install pipx

# Install contextr globally (when published)
pipx install contextr

# Or install from source
pipx install git+https://github.com/dharamghevariya/contextr.git
```

### For Contributors & Local Development

```bash
# Clone the repository
git clone https://github.com/dharamghevariya/contextr.git
cd contextr

# Method 1: Using pipx (Recommended)
pipx install -e .

# Method 2: Using uv (for development)
uv sync
# Then use: uv run contextr

# Method 3: Using pip in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Usage

### Basic Examples

```bash
# After installing with pipx
contextr .

# Package a specific directory
contextr /path/to/your/project

# Package specific files
contextr src/main.py src/utils.py

# Save output to a file
contextr . -o my-project-context.txt

# Include only Python files
contextr . --include "*.py"

# Include only JavaScript files
contextr . --include "*.js"
```

### Using with uv (Development)

```bash
# Package the current directory
uv run contextr .

# Package with filters
uv run contextr . --include "*.py" -o output.txt
```

### Using with virtual environment

```bash
# After activating your virtual environment
python -m contextr .
# Or if installed in the environment
contextr .
```

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `paths` | - | One or more file or directory paths to analyze | `contextr src/ docs/` |
| `--output` | `-o` | Output file path (default: stdout) | `-o context.txt` |
| `--include` | - | Pattern to include files (glob pattern) | `--include "*.py"` |
| `--version` | `-v` | Show version and exit | `-v` |
| `--help` | `-h` | Show help message | `-h` |

### Advanced Examples

```bash
# Package only Python and JavaScript files
contextr . --include "*.{py,js}"

# Package a specific subdirectory
contextr src/ --include "*.py" -o backend-context.txt

# Package multiple specific files
contextr README.md src/main.py pyproject.toml

# Analyze a different repository
contextr /path/to/other/project -o other-project.txt
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

### 5. Summary Statistics
- Total number of files processed
- Total lines of code

## Example Output

When you run `contextr . --include "*.py"`, the output looks like this:

```
# Repository Context

## File System Location

/home/user/my-project

## Git Info

- Commit: a1b2c3d4e5f6789...
- Branch: main  
- Author: John Doe <john@example.com>
- Date: Fri Sep 12 14:30:15 2025 -0400

## Structure

src/
  main.py
  utils/
    helpers.py
package.json
README.md

## File Contents

### File: src/main.py
```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

### File: package.json
```json
{
  "name": "my-project",
  "version": "1.0.0"
}
```

## Summary
- Total files: 2
- Total lines: 8
```

## 🔍 What Files Are Included

The tool includes most text files but automatically excludes:

### 📁 Excluded Directories
- `.git`, `.svn`, `.hg` (version control)
- `__pycache__`, `.pytest_cache` (Python cache)
- `node_modules`, `.npm` (Node.js)
- `.vscode`, `.idea` (IDE directories)
- `build`, `dist`, `target` (build directories)
- `.env`, `venv`, `.venv` (virtual environments)

### 📄 File Handling Rules
- **Binary files**: Automatically detected and skipped
- **Large files**: Files larger than 16KB are truncated with notice
- **Permission errors**: Skipped with warning message to stderr
- **Text files**: All readable text files are included by default

### 🎯 Pattern Matching
Use the `--include` option to filter files:
- `--include "*.py"` - Only Python files
- `--include "*.{js,ts}"` - JavaScript and TypeScript files
- `--include "*.md"` - Only Markdown files

## ⚠️ Error Handling

The tool handles errors gracefully:

| Error Type | Behavior | Example |
|------------|----------|---------|
| **Permission errors** | Skipped with warning message | `Warning: Permission denied: /restricted/file.txt` |
| **Binary files** | Automatically detected and skipped | `.exe`, `.jpg`, `.pdf` files ignored |
| **Large files** | Truncated with clear notice | `[File truncated - original size: 25KB]` |
| **Invalid paths** | Clear error messages | `Error: Path does not exist: /invalid/path` |
| **Non-git repositories** | Works fine | Shows "Not a git repository" in output |
| **Network issues** | Graceful fallback | Git info shows as unavailable |

## 🛠️ Development

### Project Structure

```
contextr/
├── main.py                    # Entry point script
├── pyproject.toml            # Project configuration & dependencies
├── README.md                 # This documentation
├── LICENSE                   # MIT License
├── uv.lock                   # Dependency lock file
└── src/
    └── contextr/
        ├── __init__.py       # Package initialization
        ├── cli.py           # CLI interface using Typer
        ├── commands/
        │   ├── __init__.py
        │   └── package.py   # Main packaging logic
        └── utils/
            ├── __init__.py
            └── helpers.py   # Utility functions
```

### 🧪 Running Tests

```bash
# Install development dependencies
uv sync --dev

# Run tests (when available)
uv run pytest

# Run linting
uv run flake8 src/

# Run type checking
uv run mypy src/

# Format code
uv run black src/
```

### 🚀 Contributing

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/contextr.git
   cd contextr
   ```
3. **Install for development:**
   ```bash
   pipx install -e .
   ```
4. **Make your changes and test:**
   ```bash
   contextr . --include "*.py"
   ```
5. **Submit a pull request**

### 📋 Development Workflow

```bash
# 1. Setup development environment
git clone https://github.com/dharamghevariya/contextr.git
cd contextr
uv sync

# 2. Make changes to the code
# Edit files in src/contextr/

# 3. Test your changes
uv run contextr . --include "*.py"

# 4. Install in development mode for system-wide testing
pipx install -e .

# 5. Test the installed version
contextr . -o test-output.txt
```

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤔 Why contextr?

The name "contextr" combines "context" + "r" (for repository), representing the tool's purpose of providing rich context about code repositories in a format that's perfect for LLM interactions.

### 💡 Use Cases

- **Code Reviews**: Share complete project context with team members
- **AI Assistance**: Get better help from ChatGPT, Claude, or GitHub Copilot
- **Documentation**: Create comprehensive project snapshots
- **Onboarding**: Help new team members understand project structure
- **Debugging**: Share complete context when asking for help

### 🎯 Perfect for LLMs

The output format is specifically designed to work well with Large Language Models:
- Clear section headers for easy parsing
- Syntax highlighting markers for code blocks
- Structured metadata (git info, file locations)
- Complete project context in a single file
- Optimized for token efficiency

---

**Made with ❤️ for developers who want better AI assistance with their code.**

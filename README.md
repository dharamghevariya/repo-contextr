# contextr

A Repository Context Packager CLI tool that analyzes local git repositories and creates text files containing repository content optimized for sharing with Large Language Models (LLMs).

## Overview

When developers want to get help from ChatGPT or other LLMs about their code, they often struggle with how to share their codebase effectively. They might copy-paste individual files, but this loses important context about the project structure, dependencies, and relationships between files. 

`contextr` solves this by automatically collecting and formatting repository content into a single, well-structured text file that can be easily shared with any LLM.

## Features

- **Git Integration**: Extracts commit SHA, branch, author, and date information
- **Project Structure**: Generates a clear directory tree visualization
- **File Content Packaging**: Includes file contents with syntax highlighting
- **Smart File Discovery**: Recursively scans directories with configurable filtering
- **Large File Handling**: Truncates files larger than 16KB with clear notices
- **Binary File Detection**: Automatically skips binary files
- **Error Handling**: Gracefully handles permission errors and provides helpful messages
- **Flexible Output**: Write to stdout or save to a file

## Installation

### Prerequisites

- Python 3.12 or higher
- Git (for git repository analysis)

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

## Usage

### Basic Examples

```bash
# Package the current directory
uv run main.py .

# Package a specific directory
uv run main.py /path/to/your/project

# Package specific files
uv run main.py src/main.py src/utils.py

# Save output to a file
uv run main.py . -o my-project-context.txt

# Include only Python files
uv run main.py . --include "*.py"

# Include only JavaScript files
uv run main.py . --include "*.js"
```

### Command Line Options

- `paths` - One or more file or directory paths to analyze (default: current directory)
- `-o, --output` - Output file path (default: stdout)
- `--include` - Pattern to include files (e.g., '*.py', '*.js')
- `-v, --version` - Show version and exit
- `-h, --help` - Show help message

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

```markdown
# Repository Context

## File System Location

/home/user/my-project

## Git Info

- Commit: a1b2c3d4e5f6789...
- Branch: main  
- Author: John Doe <john@example.com>
- Date: Fri Sep 12 14:30:15 2025 -0400

## Structure
```
src/
  main.py
  utils/
    helpers.py
package.json
README.md
```

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

## What Files Are Included

The tool includes most text files but automatically excludes:

### Directories
- `.git`, `.svn`, `.hg` (version control)
- `__pycache__`, `.pytest_cache` (Python cache)
- `node_modules`, `.npm` (Node.js)
- `.vscode`, `.idea` (IDE directories)
- `build`, `dist`, `target` (build directories)
- `.env`, `venv`, `.venv` (virtual environments)

### Files
- Binary files (detected by null bytes)
- Files larger than 16KB (truncated with notice)
- Files you don't have permission to read (logged to stderr)

## Error Handling

The tool handles errors gracefully:

- **Permission errors**: Skipped with warning message
- **Binary files**: Automatically detected and skipped
- **Large files**: Truncated with clear notice
- **Invalid paths**: Clear error messages
- **Non-git repositories**: Works fine, just shows "Not a git repository"

## Development

### Project Structure

```
contextr/
├── main.py                 # Main entry point
├── pyproject.toml         # Project configuration
├── README.md              # This file
├── LICENSE                # MIT License
└── src/
    └── contextr/
        ├── __init__.py
        ├── cli.py         # CLI interface
        ├── commands/
        │   ├── __init__.py
        │   └── package.py # Main packaging logic
        └── utils/
            ├── __init__.py
            └── helpers.py # Helper utilities
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Why contextr?

The name "contextr" combines "context" + "r" (for repository), representing the tool's purpose of providing rich context about code repositories in a format that's perfect for LLM interactions.

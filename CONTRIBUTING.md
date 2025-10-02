# Contributing to repo-contextr

Thank you for your interest in contributing to repo-contextr! This guide will help you get started with development and contributing to the project.

## Getting Started

### Prerequisites

- **Python 3.12+**: Make sure you have Python 3.12 or higher installed
- **Git**: For version control
- **uv**: Fast Python package installer and resolver (recommended)

### Installing uv

We recommend using `uv` for package management and development. It's much faster than pip and handles virtual environments automatically.

**Download and Install uv:**

Visit the official uv installation page: **https://docs.astral.sh/uv/getting-started/installation/**

**Quick installation options:**

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip (if you prefer)
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using Cargo (Rust)
cargo install uv
```

## Development Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/repo-contextr.git
cd repo-contextr
```

### 2. Set Up Development Environment

```bash
# Install dependencies and create virtual environment
uv sync

# This automatically:
# - Creates a virtual environment
# - Installs all dependencies from pyproject.toml
# - Installs development dependencies
```

### 3. Verify Installation

```bash
# Test the installation
uv run repo-contextr --help

# Run on current directory
uv run repo-contextr . --include "*.py"
```

## Running Tests

```bash
# Run all tests
uv run python -m pytest

# Run specific test file
uv run python src/tests/test_toml.py

# Run tests with verbose output
uv run python -m pytest -v

# Run tests for specific functionality
uv run python src/tests/test_toml.py
uv run python src/tests/test_unrecognized_options.py
```

## Development Commands

### Running the Tool

```bash
# Run the development version
uv run repo-contextr .

# Run with specific options
uv run repo-contextr . --include "*.py" --output test.txt

# Run with recent changes only
uv run repo-contextr . --recent
```

### Code Quality

```bash
# Format code with black (when available)
uv run black src/

# Run type checking with mypy (when available)
uv run mypy src/

# Run linting with flake8 (when available)
uv run flake8 src/
```

### Adding Dependencies

```bash
# Add a new runtime dependency
uv add package-name

# Add a new development dependency
uv add --dev package-name

# Add a specific version
uv add "package-name>=1.0.0"
```

## Project Structure

```
repo-contextr/
├── src/
│   ├── contextr/
│   │   ├── __init__.py          # Package initialization
│   │   ├── cli.py               # CLI interface and TOML config
│   │   ├── main.py              # Entry point
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   └── package.py       # Main packaging logic
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py       # Utility functions
│   └── tests/
│       ├── test_toml.py         # TOML configuration tests
│       ├── test_recent.py       # Recent changes tests
│       └── test_unrecognized_options.py
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
├── README.md                    # Project documentation
└── CONTRIBUTING.md              # This file
```

## How to Contribute

### 1. Find Something to Work On

- Check the [Issues](https://github.com/BHChen24/repo-contextr/issues) tab for open issues
- Look for issues labeled `good first issue` or `help wanted`
- Found a bug? Create a new issue describing it
- Have a feature idea? Open an issue to discuss it first

### 2. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 3. Make Your Changes

- Write clear, readable code
- Add tests for new functionality
- Update documentation if needed
- Follow existing code style and patterns

### 4. Test Your Changes

```bash
# Run tests to make sure nothing is broken
uv run python src/tests/test_toml.py

# Test the CLI manually
uv run repo-contextr . --include "*.py"

# Test with different configurations
uv run repo-contextr . --recent --output test.txt
```

### 5. Commit and Push

```bash
# Add your changes
git add .

# Commit with a clear message
git commit -m "Add: description of your changes"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template with:
   - Clear description of changes
   - Link to related issue (if any)
   - Testing steps
   - Screenshots (if UI changes)

## Testing Guidelines

### Writing Tests

- Add tests for any new functionality
- Test both success and error cases
- Use descriptive test function names
- Mock external dependencies when needed

Example test structure:
```python
def test_feature_with_valid_input():
    """Test that feature works correctly with valid input"""
    # Arrange
    input_data = "test input"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_output
```

### Configuration Testing

When working with TOML configuration:
- Test valid TOML files
- Test invalid TOML syntax
- Test missing configuration files
- Test CLI argument override behavior

## Code Style Guidelines

### General Principles

- Write clear, self-documenting code
- Use meaningful variable and function names
- Keep functions small and focused
- Add docstrings to public functions
- Handle errors gracefully

### Python Specifics

- Follow PEP 8 style guidelines
- Use type hints where helpful
- Use f-strings for string formatting
- Prefer pathlib over os.path
- Use context managers for file operations

Example:
```python
def read_config_file(config_path: Path) -> dict:
    """
    Load configuration from TOML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        typer.Exit: If file cannot be parsed
    """
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        console.print(f"❌ Invalid TOML syntax: {e}", style="bold red")
        raise typer.Exit(1)
```

## Reporting Issues

When reporting bugs, please include:

1. **Environment**: OS, Python version, uv version
2. **Steps to reproduce**: Exact commands you ran
3. **Expected behavior**: What should have happened
4. **Actual behavior**: What actually happened
5. **Error messages**: Full error output if any
6. **Configuration**: Contents of your TOML config file (if used)

Example:
```bash
# Include version information
uv --version
python --version

# Include the exact command that failed
uv run repo-contextr . --include "*.py" --output test.txt
```

## Development Workflow

### Typical Development Cycle

1. **Sync latest changes**: `git pull origin main`
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Install dependencies**: `uv sync`
4. **Make changes**: Edit code, add tests
5. **Test changes**: `uv run python src/tests/test_*.py`
6. **Manual testing**: `uv run repo-contextr . --include "*.py"`
7. **Commit changes**: `git commit -m "Add: new feature"`
8. **Push branch**: `git push origin feature/new-feature`
9. **Create PR**: Open pull request on GitHub

### Working with TOML Configuration

The tool supports TOML configuration files. Here's how to test this feature:

1. **Create a test config file**:
```toml
# test.contextr.toml
[Flags]
paths = ["src/", "tests/"]
include = "*.py"
output = "test-output.txt"
recent = false
```

2. **Test the configuration**:
```bash
# Should use config file settings
uv run repo-contextr .

# Should override config with CLI args
uv run repo-contextr . --include "*.md" --output "override.txt"
```

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Ask questions if you're unsure
- Share knowledge and best practices
- Give constructive feedback in reviews

## Resources

- **uv Documentation**: https://docs.astral.sh/uv/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **TOML Specification**: https://toml.io/
- **Typer Documentation**: https://typer.tiangolo.com/
- **Rich Documentation**: https://rich.readthedocs.io/

## Getting Help

- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README.md for usage information

Thank you for contributing to repo-contextr!
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-23

### Added
- Automated release workflow for PyPI publishing via GitHub Actions

### Changed
- Testing automated release process

## [1.0.0] - 2025-11-23

### Added
- Comprehensive test suite with 100+ tests covering all modules
- CI/CD workflow with multi-OS testing (Ubuntu, Windows, macOS)
- Token tree visualization showing distribution across directories
- File type statistics and size analytics
- Pre-commit hooks for code quality
- CHANGELOG.md for tracking releases

### Fixed
- MyPy type annotation errors
- CI pipeline dependency installation issues
- Integration test folder naming

### Changed
- Improved documentation and contributing guide

## [0.1.0] - 2025-11-XX (First PyPI Release)

### Added
- Initial release of repo-contextr
- CLI tool for packaging repository context for LLMs
- Git integration with commit SHA, branch, author, and date extraction
- Token counting and estimation feature (~4 chars per token)
- Token tree visualization showing distribution across directories
- Smart file discovery with recursive directory scanning
- Binary file detection and automatic skipping
- Recent changes mode (last 7 days) with git timestamps
- File type statistics and breakdown
- Size analytics (largest file, average file size)
- Pattern matching for file inclusion/exclusion using glob patterns
- Flexible output options (stdout or file)
- Error handling for permission issues
- Directory tree structure visualization
- Comprehensive test suite with 100+ tests
- CI/CD workflow with GitHub Actions
  - Multi-OS testing (Ubuntu, Windows, macOS)
  - Linting with Ruff
  - Type checking with MyPy
  - Test coverage reporting
- Documentation (README, CONTRIBUTING guide)
- Pre-commit hooks for code quality

### Fixed
- MyPy type annotation errors in tree formatter and statistics modules
- CI pipeline dependency installation order
- Integration test folder naming

## [0.9.0] - 2025-11-20

### Added
- Practice pre-release tag for testing release workflow

---

## Release Notes

### Version 1.0.0

This is the first stable release of **repo-contextr**, a powerful CLI tool that helps developers package their repository context for sharing with Large Language Models (LLMs) like ChatGPT, Claude, and others.

#### Key Features:
- 🚀 **Easy to Use**: Simple CLI interface with sensible defaults
- 📊 **Token Counting**: Estimate and visualize token usage across your codebase
- 🔍 **Smart Discovery**: Automatically finds and processes relevant files
- 🌲 **Tree Visualization**: Clear directory structure representation
- ⏱️ **Recent Changes**: Focus on recently modified files
- 🎯 **Pattern Matching**: Flexible file inclusion/exclusion
- ✅ **Well Tested**: Comprehensive test coverage with CI/CD
- 📝 **Rich Context**: Provides LLMs with all the context they need

#### Installation:
```bash
pip install repo-contextr
# or
pipx install repo-contextr
```

#### Usage:
```bash
# Package current directory
repo-contextr .

# Save to file
repo-contextr . -o context.txt

# Recent changes only
repo-contextr . --recent

# Include specific patterns
repo-contextr . --include "*.py"
```

#### What's Next?
- Future releases will add more features based on community feedback
- Bug fixes and improvements will be released as needed (v1.0.1, v1.0.2, etc.)
- Each release will be immutable - we never modify old releases

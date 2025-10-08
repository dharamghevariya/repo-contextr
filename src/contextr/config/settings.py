"""
Configuration settings and constants for contextr
"""

# Configuration file settings
DEFAULT_CONFIG_FILE = ".contextr.toml"
DEFAULT_PATHS = ["."]

# Default behavior
DEFAULT_RECENT = False
DEFAULT_RECENT_DAYS = 7

# File processing settings
MAX_FILE_SIZE = 16 * 1024
CHUNK_SIZE = 8192

# Skip directories
SKIP_DIRS = {
    '.git', '.svn', '.hg',  # Version control
    '__pycache__', '.pytest_cache',  # Python cache
    'node_modules', '.npm',  # Node.js
    '.vscode', '.idea',  # IDE directories
    'build', 'dist', 'target',  # Build directories
    '.env', 'venv', '.venv',  # Virtual environments
    '.mypy_cache', '.tox',  # Python tools
    'coverage', '.coverage',  # Coverage reports
    '.DS_Store', 'Thumbs.db',  # OS files
}

# Text encodings to try
TEXT_ENCODINGS = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
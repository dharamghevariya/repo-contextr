"""
Configuration module for contextr
"""

from .toml_loader import (
    ContextrConfig,
    get_effective_config
)
from .settings import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_PATHS,
    DEFAULT_RECENT,
    DEFAULT_RECENT_DAYS,
    SKIP_DIRS,
    TEXT_ENCODINGS,
    MAX_FILE_SIZE,
    CHUNK_SIZE
)
from .languages import (
    LANGUAGE_MAPPINGS,
    get_language_for_extension
)

__all__ = [
    'ContextrConfig',
    'get_effective_config',
    'DEFAULT_CONFIG_FILE',
    'DEFAULT_PATHS',
    'DEFAULT_RECENT',
    'DEFAULT_RECENT_DAYS',
    'SKIP_DIRS',
    'TEXT_ENCODINGS',
    'MAX_FILE_SIZE',
    'CHUNK_SIZE',
    'LANGUAGE_MAPPINGS',
    'get_language_for_extension'
]
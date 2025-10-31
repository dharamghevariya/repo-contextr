"""
Configuration module for contextr
"""

from .languages import LANGUAGE_MAPPINGS, get_language_for_extension
from .settings import (
    CHUNK_SIZE,
    DEFAULT_CONFIG_FILE,
    DEFAULT_PATHS,
    DEFAULT_RECENT,
    DEFAULT_RECENT_DAYS,
    MAX_FILE_SIZE,
    SKIP_DIRS,
    TEXT_ENCODINGS,
)
from .toml_loader import ContextrConfig, get_effective_config

__all__ = [
    "ContextrConfig",
    "get_effective_config",
    "DEFAULT_CONFIG_FILE",
    "DEFAULT_PATHS",
    "DEFAULT_RECENT",
    "DEFAULT_RECENT_DAYS",
    "SKIP_DIRS",
    "TEXT_ENCODINGS",
    "MAX_FILE_SIZE",
    "CHUNK_SIZE",
    "LANGUAGE_MAPPINGS",
    "get_language_for_extension",
]

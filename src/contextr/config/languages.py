"""
Language mappings for syntax highlighting.
"""

# Map file extensions to syntax highlighting language identifiers
LANGUAGE_MAPPINGS = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'jsx': 'jsx',
    'tsx': 'tsx',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'h': 'c',
    'hpp': 'cpp',
    'cs': 'csharp',
    'php': 'php',
    'rb': 'ruby',
    'go': 'go',
    'rs': 'rust',
    'swift': 'swift',
    'kt': 'kotlin',
    'scala': 'scala',
    'sh': 'bash',
    'bash': 'bash',
    'zsh': 'zsh',
    'fish': 'fish',
    'ps1': 'powershell',
    'html': 'html',
    'htm': 'html',
    'xml': 'xml',
    'css': 'css',
    'scss': 'scss',
    'sass': 'sass',
    'less': 'less',
    'json': 'json',
    'yaml': 'yaml',
    'yml': 'yaml',
    'toml': 'toml',
    'ini': 'ini',
    'cfg': 'ini',
    'conf': 'ini',
    'md': 'markdown',
    'markdown': 'markdown',
    'rst': 'rst',
    'txt': 'text',
    'sql': 'sql',
    'dockerfile': 'dockerfile',
    'makefile': 'makefile',
    'r': 'r',
    'rmd': 'rmarkdown',
    'tex': 'latex',
    'vim': 'vim',
    'lua': 'lua',
    'pl': 'perl',
    'pm': 'perl',
}


def get_language_for_extension(extension: str) -> str:
    """
    Map file extension to syntax highlighting language.
    
    Args:
        extension: File extension (without the dot)
        
    Returns:
        Language identifier for syntax highlighting, or empty string if unknown
    """
    return LANGUAGE_MAPPINGS.get(extension.lower(), '')
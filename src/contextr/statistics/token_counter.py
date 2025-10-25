"""
Token counting and estimation functionality.

Uses the approximation of ~4 characters per token for English text,
which is a common heuristic for LLM token estimation.
"""
from pathlib import Path
from typing import Dict, List, Optional

from ..processing import read_file_content, is_binary_file


# Token estimation constant: ~4 characters per token
CHARS_PER_TOKEN = 4.0


class TokenCounter:
    """Handles token counting and estimation for files and directories."""
    
    def __init__(self, chars_per_token: float = CHARS_PER_TOKEN):
        """
        Initialize the token counter.
        
        Args:
            chars_per_token: Characters per token ratio (default: 4.0)
        """
        self.chars_per_token = chars_per_token
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        char_count = len(text)
        return int(char_count / self.chars_per_token)
    
    def count_file_tokens(self, file_path: Path) -> Optional[int]:
        """
        Count tokens in a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Token count or None if file cannot be read
        """
        try:
            # Skip binary files
            if is_binary_file(file_path):
                return 0
            
            content = read_file_content(file_path)
            if content is None:
                return None
            
            return self.estimate_tokens(content)
            
        except Exception:
            return None
    
    def count_files_tokens(self, files: List[Path]) -> Dict[Path, int]:
        """
        Count tokens for multiple files.
        
        Args:
            files: List of file paths to analyze
            
        Returns:
            Dictionary mapping file paths to their token counts
        """
        token_counts = {}
        
        for file_path in files:
            token_count = self.count_file_tokens(file_path)
            if token_count is not None:
                token_counts[file_path] = token_count
        
        return token_counts
    
    def build_token_tree(
        self,
        files: List[Path],
        repo_root: Path,
        threshold: int = 0
    ) -> Dict:
        """
        Build a hierarchical token count tree structure.
        
        Args:
            files: List of file paths to analyze
            repo_root: Repository root path
            threshold: Minimum token count to include (0 = include all)
            
        Returns:
            Nested dictionary representing the token tree structure
        """
        # Count tokens for all files
        token_counts = self.count_files_tokens(files)
        
        # Filter by threshold
        if threshold > 0:
            token_counts = {
                path: count for path, count in token_counts.items()
                if count >= threshold
            }
        
        # Build the tree structure
        tree = {}
        total_tokens = 0
        
        for file_path, token_count in token_counts.items():
            try:
                relative_path = file_path.relative_to(repo_root)
                parts = relative_path.parts
                
                # Navigate/create the tree structure
                current = tree
                for i, part in enumerate(parts[:-1]):  # All but the last part (directories)
                    if part not in current:
                        current[part] = {
                            '_tokens': 0,
                            '_type': 'directory',
                            '_children': {}
                        }
                    current = current[part]['_children']
                
                # Add the file
                if parts:
                    filename = parts[-1]
                    current[filename] = {
                        '_tokens': token_count,
                        '_type': 'file'
                    }
                
                total_tokens += token_count
                
            except ValueError:
                # File is outside repo_root, skip it
                continue
        
        # Calculate directory totals (bottom-up)
        self._calculate_directory_totals(tree)
        
        return {
            'tree': tree,
            'total_tokens': total_tokens,
            'file_count': len(token_counts),
            'threshold': threshold
        }
    
    def _calculate_directory_totals(self, tree: Dict) -> int:
        """
        Recursively calculate token totals for directories.
        
        Args:
            tree: Tree structure to process
            
        Returns:
            Total tokens in this tree/subtree
        """
        total = 0
        
        for key, value in tree.items():
            if isinstance(value, dict):
                if value.get('_type') == 'file':
                    total += value.get('_tokens', 0)
                elif value.get('_type') == 'directory':
                    # Recursively calculate for subdirectories
                    subtree_total = self._calculate_directory_totals(value.get('_children', {}))
                    value['_tokens'] = subtree_total
                    total += subtree_total
        
        return total
    
    def format_token_count(self, count: int) -> str:
        """
        Format token count with thousands separator.
        
        Args:
            count: Token count
            
        Returns:
            Formatted string (e.g., "1,247" or "70,925")
        """
        return f"{count:,}"

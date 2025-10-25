"""
Token count tree visualization formatter.

Generates hierarchical tree structures showing token distribution
across directories and files.
"""
from pathlib import Path
from typing import Dict, List


class TokenTreeFormatter:
    """Formats token count data as a hierarchical tree visualization."""
    
    def __init__(self):
        """Initialize the token tree formatter."""
        pass
    
    def format_tree(
        self,
        tree_data: Dict,
        repo_root: Path
    ) -> str:
        """
        Format token tree data into a visual tree structure.
        
        Args:
            tree_data: Token tree data from TokenCounter.build_token_tree()
            repo_root: Repository root path for the header
            
        Returns:
            Formatted tree string
        """
        output_parts = []
        
        # Header
        output_parts.append("# Token Count Tree\n")
        output_parts.append(f"**Repository:** {repo_root}\n")
        
        # Metadata
        total_tokens = tree_data.get('total_tokens', 0)
        file_count = tree_data.get('file_count', 0)
        threshold = tree_data.get('threshold', 0)
        
        output_parts.append(f"**Total Tokens:** {total_tokens:,}")
        output_parts.append(f"**Files Analyzed:** {file_count}")
        
        if threshold > 0:
            output_parts.append(f"**Threshold:** {threshold:,} tokens (showing only files/dirs above threshold)\n")
        else:
            output_parts.append("")
        
        # Tree visualization
        tree = tree_data.get('tree', {})
        if tree:
            output_parts.append("## Token Distribution\n")
            output_parts.append("```")
            
            # Start with root
            root_name = repo_root.name or str(repo_root)
            root_tokens = sum(
                self._get_node_tokens(node)
                for node in tree.values()
            )
            output_parts.append(f"{root_name}/ ({root_tokens:,} tokens)")
            
            # Format the tree recursively
            tree_lines = self._format_tree_recursive(tree, "", True)
            output_parts.extend(tree_lines)
            
            output_parts.append("```")
        else:
            output_parts.append("No files found or all files below threshold.")
        
        return "\n".join(output_parts)
    
    def _format_tree_recursive(
        self,
        tree: Dict,
        prefix: str = "",
        is_last: bool = True
    ) -> List[str]:
        """
        Recursively format tree structure with proper indentation.
        
        Args:
            tree: Tree dictionary to format
            prefix: Current line prefix for indentation
            is_last: Whether this is the last item in current level
            
        Returns:
            List of formatted tree lines
        """
        lines = []
        
        # Sort items: directories first (alphabetically), then files (by token count descending)
        items = []
        for key, value in tree.items():
            if isinstance(value, dict):
                node_type = value.get('_type', 'unknown')
                tokens = value.get('_tokens', 0)
                items.append((key, value, node_type, tokens))
        
        # Sort: directories first (alphabetically), then files by token count (descending)
        items.sort(key=lambda x: (
            0 if x[2] == 'directory' else 1,  # directories first
            -x[3] if x[2] == 'file' else x[0].lower()  # files by tokens desc, dirs by name
        ))
        
        for i, (name, node, node_type, tokens) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            
            # Choose the appropriate tree characters
            if is_last_item:
                connector = "└── "
                extension = "    "
            else:
                connector = "├── "
                extension = "│   "
            
            # Format the line
            if node_type == 'directory':
                line = f"{prefix}{connector}{name}/ ({tokens:,} tokens)"
                lines.append(line)
                
                # Recursively format children
                children = node.get('_children', {})
                if children:
                    child_lines = self._format_tree_recursive(
                        children,
                        prefix + extension,
                        is_last_item
                    )
                    lines.extend(child_lines)
                    
            elif node_type == 'file':
                line = f"{prefix}{connector}{name} ({tokens:,} tokens)"
                lines.append(line)
        
        return lines
    
    def _get_node_tokens(self, node: Dict) -> int:
        """
        Get token count for a node.
        
        Args:
            node: Tree node dictionary
            
        Returns:
            Token count for this node
        """
        if isinstance(node, dict):
            return node.get('_tokens', 0)
        return 0
    
    def format_summary(self, tree_data: Dict) -> str:
        """
        Format a simple summary of token counts without tree visualization.
        
        Args:
            tree_data: Token tree data
            
        Returns:
            Formatted summary string
        """
        total_tokens = tree_data.get('total_tokens', 0)
        file_count = tree_data.get('file_count', 0)
        
        return f"Estimated tokens: {total_tokens:,} (across {file_count} files)"

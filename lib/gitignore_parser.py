import os

DEFAULT_IGNORE_PATTERNS = [
    "__pycache__",
    "venv",
    ".git",
    ".DS_Store",
    ".arcode.cache.pkl",
    ".arcode.checksum.txt",
    ".arcode.embeddings",
    ".env",
    "node_modules",
]

def parse_gitignore(gitignore_path, additional_patterns=None):
    """
    Parse the .gitignore file and combine it with additional ignore patterns.

    Args:
        gitignore_path (str): Path to the .gitignore file.
        additional_patterns (list, optional): List of additional ignore patterns. Defaults to None.

    Returns:
        set: A set of combined ignore patterns.
    """
    if not os.path.exists(gitignore_path):
        ignore_patterns = set(DEFAULT_IGNORE_PATTERNS)
    else:
        with open(gitignore_path, 'r') as file:
            lines = file.readlines()
        ignore_patterns = set(DEFAULT_IGNORE_PATTERNS)
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                ignore_patterns.add(line)

    if additional_patterns:
        if isinstance(additional_patterns, str):
            additional_patterns = [additional_patterns]
        ignore_patterns.update(additional_patterns)

    return ignore_patterns

def is_ignored(path, ignore_patterns):
    """
    Check if the given path matches any of the ignore patterns.

    Args:
        path (str): The path to check.
        ignore_patterns (set): A set of ignore patterns.

    Returns:
        bool: True if the path matches any ignore patterns, False otherwise.
    """
    for pattern in ignore_patterns:
        if path.endswith(f"/{pattern}") or path.startswith(pattern) or path.startswith(f"./{pattern}") or f"/{pattern}/" in path:
            return True
    return False
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
    for pattern in ignore_patterns:
        if path.endswith(f"/{pattern}") or path.startswith(pattern) or path.startswith(f"./{pattern}") or f"/{pattern}/" in path:
            return True
    return False
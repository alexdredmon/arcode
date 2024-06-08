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

def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return set()

    with open(gitignore_path, 'r') as file:
        lines = file.readlines()

    ignore_patterns = set(DEFAULT_IGNORE_PATTERNS)
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            ignore_patterns.add(line)
    return ignore_patterns

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if path.startswith(pattern) or path.startswith(f"./{pattern}") or f"/{pattern}/" in path:
            return True
    return False

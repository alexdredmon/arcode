import os

def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return set()

    with open(gitignore_path, 'r') as file:
        lines = file.readlines()

    ignore_patterns = set()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            ignore_patterns.add(line)
    return ignore_patterns

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if path.startswith(pattern):
            return True
    return False

import hashlib
import os
from .gitignore_parser import is_ignored

def calculate_directory_checksum(directory, ignore_patterns):
    hash_obj = hashlib.sha256()
    
    for root, _, files in os.walk(directory):
        files = [f for f in files if not is_ignored(os.path.relpath(os.path.join(root, f), directory), ignore_patterns)]
        
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as file:
                    while chunk := file.read(8192):
                        hash_obj.update(chunk)
            except OSError as e:
                print(f"Error reading file {filepath}: {e}")
    
    return hash_obj.hexdigest()

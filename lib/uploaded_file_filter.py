"""
This module provides functionality to filter uploaded files based on predefined and custom ignore
patterns.
It leverages patterns from a project's .gitignore file, a set of default ignore patterns, and any
additional patterns provided by the user to determine which files should be excluded from
processing.

Classes:
    UploadedFileFilter: Initializes with a starting path and optional additional ignore patterns.
    It can then be used to filter a list of files, excluding those that match the ignore patterns.

Constants:
    DEFAULT_IGNORE_PATTERNS: A list of file and directory patterns to be ignored by default.
"""
import os
import pathspec
from lib.file_io import is_binary_file
from lib.shell_util import LIGHT_BLUE, LIGHT_PINK, LIGHT_RED, RESET_COLOR

DEFAULT_IGNORE_PATTERNS = [
    "**/.git/**",
    "**/.github/**",
    "**/.next/**",
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/venv/**",
    "**/.arcode.cache.pkl",
    "**/.arcode.checksum.txt",
    "**/.arcode.embeddings",
    "**/.DS_Store",
    "**/.env",
    "**/package-lock.json"
]

class UploadedFileFilter:
    """
    A class to filter uploaded files based on ignore patterns.

    This class uses ignore patterns from the project's .gitignore file, a set of default ignore
    patterns, and any additional patterns provided by the user to determine which files should be
    excluded from processing. It is initialized with a starting path and can optionally include
    additional ignore patterns.

    Attributes:
        startpath (str): The starting path from which to filter files.
        gitignore_path (str): The path to the .gitignore file within the startpath.
        patterns (List[str]): A list of ignore patterns compiled from the .gitignore file, default
            ignore patterns, and any additional patterns provided by the user.
        max_file_size (int): The maximum allowed file size in bytes.

    Methods:
        __init__(self, startpath, additional_patterns=None, max_file_size=1000000): Initializes the UploadedFileFilter
            with a starting path, optional additional ignore patterns, and maximum file size.
    """
    def __init__(self, startpath, additional_patterns=None, max_file_size=1000000):
        self.startpath = startpath
        self.gitignore_path = os.path.join(startpath, ".gitignore")
        self.patterns = DEFAULT_IGNORE_PATTERNS.copy()
        self.max_file_size = max_file_size

        # Add patterns from .gitignore if it exists
        if os.path.exists(self.gitignore_path):
            with open(self.gitignore_path, 'r', encoding='utf-8') as ignore_file:
                for line in ignore_file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.patterns.append(line)

        if additional_patterns:
            self.patterns.extend(additional_patterns)

        self.spec = pathspec.GitIgnoreSpec.from_lines(self.patterns)

    def select_files(self, files):
        """
        Filter files based on the .gitignore file and additional patterns.

        Args:
            files (list): A list of file paths.

        Returns:
            list: A list of file paths that should be uploaded.
        """
        return [f for f in files if self.should_upload(f)]

    def should_upload(self, file):
        """
        Check if the file should be uploaded.

        Args:
            file (str): A file path, relative to the start directory.

        Returns:
            bool: True if the file is not excluded by the .gitignore file, any
                  additional patterns, is not a binary file, and does not exceed
                  the maximum file size limit. False otherwise.
        """
        path = os.path.normpath(file)
        full_path = os.path.join(self.startpath, path)

        if self.spec.match_file(path):
            return False

        if is_binary_file(full_path):
            return False

        if os.path.getsize(full_path) > self.max_file_size:
            print(f" ❗️ {LIGHT_BLUE}Skipping {LIGHT_RED}{full_path}{LIGHT_BLUE}: File size exceeds maximum limit.{RESET_COLOR}")
            return False

        return True
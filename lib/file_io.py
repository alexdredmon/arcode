import os
from .gitignore_parser import is_ignored
import magic
from collections import defaultdict

from .constants import binary_extensions
from .file_parser import (
    extract_filename_start,
    extract_filename_end,
    format_file_contents,
    parse_files,
    is_in_middle_of_file,
    extract_estimated_characters
)
from .shell_util import (
    LIGHT_BLUE, LIGHT_PINK, LIGHT_GREEN, RESET_COLOR
)

def is_binary_file(filename):
    """
    Check if a given filename is a binary file based on its extension and MIME type,
    excluding specific MIME types like application/xhtml+xml and application/xml.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    if os.path.splitext(filename)[1].lower() in binary_extensions:
        return True
    magic_obj = magic.Magic(mime=True)
    mime_type = magic_obj.from_file(filename)

    # Exclude specific MIME types that should not be considered binary
    excluded_mime_types = ['application/xhtml+xml', 'application/xml', 'application/json', 'application/javascript']
    if mime_type in excluded_mime_types:
        return False

    return ('application/' in mime_type or
            'image/' in mime_type or
            'audio/' in mime_type or
            'video/' in mime_type)

def print_files_as_tree(startpath, relative_paths):
    """
    Given an unordered iterable of paths, prints the files as an ordered
    tree relative to the startpath.

    Args:
        startpath (str): The starting directory path.
        relative_paths (list): List of relative paths for uploaded files.
    """

    tree = lambda: defaultdict(tree)
    root = tree()

    # Build the tree structure
    for path in relative_paths:
        parts = path.split(os.sep)
        current_level = root
        for part in parts:
            current_level = current_level[part]

    # Print the tree structure
    print_tree_structure(root)

def print_tree_structure(root, level=0):
    for key in sorted(root.keys()):
        print(' ' * 4 * level + key)
        print_tree_structure(root[key], level + 1)

def print_tree(startpath, ignore_patterns, prefix=""):
    """
    Print the directory tree starting from the given path, ignoring specific patterns.

    Args:
        startpath (str): The starting directory path.
        ignore_patterns (list): List of patterns to ignore during directory scan.
        prefix (str, optional): Prefix string for formatting the tree. Defaults to "".
    """
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [
            d
            for d in dirs
            if not is_ignored(
                os.path.relpath(os.path.join(root, d), startpath),
                ignore_patterns,
            )
        ]
        files = [
            f
            for f in files
            if not is_ignored(
                os.path.relpath(os.path.join(root, f), startpath),
                ignore_patterns,
            )
            and not is_binary_file(os.path.relpath(os.path.join(root, f), startpath))
        ]

        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{prefix}{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{prefix}{subindent}{f}")

def get_files(startpath, upload_filter):
    """
    Retrieve files from the given starting path, ignoring specific patterns, binary files, and files exceeding max size.

    Args:
        startpath (str): The starting directory path.
        upload_filter (UploadedFileFilter): Filter object for file upload decisions.

    Returns:
        list: List of dictionaries containing file paths and data.
    """
    print(f"{LIGHT_BLUE} 🕰️  Scanning your codebase...{RESET_COLOR}")
    all_files = []
    for root, _, files in os.walk(startpath):
        files = [
            f
            for f in files
            if upload_filter.should_upload(os.path.relpath(os.path.join(root, f), startpath))
        ]
        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), startpath)
            full_path = os.path.join(root, f)
            try:
                with open(
                    full_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore",
                ) as file:
                    all_files.append(
                        {
                            "path": file_path,
                            "data": file.read(),
                        }
                    )
            except UnicodeDecodeError as e:
                print(f"Error reading file {file_path}: {e}")
            except Exception as e:
                print(f"Unknown error reading file: {file_path}: {e}")
    return all_files

def calculate_line_difference(filepath, new_content):
    """
    Calculate the line difference between the current and new content of a file.

    Args:
        filepath (str): The file path.
        new_content (str): The new file content.

    Returns:
        int: The difference in the number of lines.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            current_content = file.read()
        current_lines = current_content.count("\n")
        new_lines = new_content.count("\n")
        return new_lines - current_lines
    except FileNotFoundError:
        return len(
            new_content.splitlines()
        )  # If file does not exist, return total lines as added

def write_files(files, base_dir, debug=False):
    """
    Write the provided file contents into the specified base directory.

    Args:
        files (list): List of files with filenames and contents.
        base_dir (str): The base directory where the files should be written.
        debug (bool): Flag to enable debug output.

    Returns:
        list: List of paths of the written files.
    """
    written_files = []
    for file in files:
        try:
            file_path = os.path.join(base_dir, file["filename"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if debug:
                print(f"Debug: Writing file: {file_path}")
                print(f"Debug: Content preview: {file['contents'][:50]}...")
            
            with open(file_path, "w", encoding="utf-8", newline='') as f:
                f.write(file["contents"])
            
            print(f"Successfully wrote file: {file_path}")
            written_files.append(file_path)
        except Exception as e:
            print(f"Error writing file {file['filename']}:\n{e}")

    if debug:
        print(f"Debug: Finished writing {len(files)} files")

    return written_files
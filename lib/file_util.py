import os
from .gitignore_parser import is_ignored
from .file_type_util import is_binary_file

def print_tree(startpath, ignore_patterns, prefix=""):
    """
    Print the directory tree starting from the given path, ignoring specific patterns.
    This function is cross-platform compatible.

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
            and not is_binary_file(os.path.join(root, f))
        ]

        level = len(os.path.relpath(root, startpath).split(os.sep))
        indent = " " * 4 * (level - 1)
        print(f"{prefix}{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * level
        for f in files:
            print(f"{prefix}{subindent}{f}")

def get_files(startpath, ignore_patterns):
    """
    Retrieve files from the given starting path, ignoring specific patterns and binary files.
    This function is cross-platform compatible.

    Args:
        startpath (str): The starting directory path.
        ignore_patterns (list): List of patterns to ignore during file search.

    Returns:
        list: List of dictionaries containing file paths and data.
    """
    all_files = []
    for root, _, files in os.walk(startpath):
        files = [
            f
            for f in files
            if not is_ignored(
                os.path.relpath(os.path.join(root, f), startpath),
                ignore_patterns,
            )
            and not is_binary_file(os.path.join(root, f))
        ]
        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), startpath)
            try:
                with open(
                    os.path.join(root, f),
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
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    return all_files

def calculate_line_difference(filepath, new_content):
    """
    Calculate the line difference between the current and new content of a file.
    This function is cross-platform compatible.

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
    This function is cross-platform compatible.

    Args:
        files (list): List of files with filenames and contents.
        base_dir (str): The base directory where the files should be written.
        debug (bool): Flag to enable debug output.
    """
    for file in files:
        try:
            file_path = os.path.join(base_dir, file["filename"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if debug:
                print(f"Debug: Writing file: {file_path}")
                print(f"Debug: Content preview: {file['contents'][:50]}...")

            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(file["contents"])

            print(f"Successfully wrote file: {file_path}")
        except Exception as e:
            print(f"Error writing file {file['filename']}:\n{e}")

    if debug:
        print(f"Debug: Finished writing {len(files)} files")
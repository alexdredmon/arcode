import os
import re
from .gitignore_parser import is_ignored

from .constants import binary_extensions

# Updated regex to be more inclusive
file_parse_pattern = re.compile(
    r"===\.= ==== FILENAME: (?P<filename>.*?) = ===== =========\n(?:```(?:.*?)\n)?(?P<content>.*?)\n(?:```\n)?===\.= ==== EOF: (?P=filename) = ===== =========",
    re.DOTALL,
)

# Define the pattern for the starting token
middle_of_file_start_pattern = re.compile(
    r"===\.= ==== FILENAME: .*? = ===== =========\n(?:```.*?\n)?", re.DOTALL
)
# Define the pattern for the closing token
middle_of_file_end_pattern = re.compile(
    r"(?:```\n)?===\.= ==== EOF: .*? = ===== =========\n", re.DOTALL
)

file_start_token = re.compile(
    r"===\.= ==== FILENAME: (.*?) = ===== =========", re.DOTALL
)

file_end_token = re.compile(
    r"===\.= ==== EOF: (.*?) = ===== =========", re.DOTALL
)


def extract_filename_start(text):
    """
    Extract the filename from the start token in the text.

    Args:
        text (str): The text containing the filename start token.

    Returns:
        str: The extracted filename or None if not found.
    """
    matches = file_start_token.findall(text)
    if len(matches) == 1:
        return matches[0]
    else:
        return None


def extract_filename_end(text):
    """
    Extract the filename from the end token in the text.

    Args:
        text (str): The text containing the filename end token.

    Returns:
        str: The extracted filename or None if not found.
    """
    matches = file_end_token.findall(text)
    if len(matches) == 1:
        return matches[0]
    else:
        return None


def is_binary_file(filename):
    """
    Check if a given filename is a binary file based on its extension.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    return os.path.splitext(filename)[1].lower() in binary_extensions


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
            and not is_binary_file(f)
        ]

        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{prefix}{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{prefix}{subindent}{f}")


def format_file_contents(files):
    """
    Format the file contents for display.

    Args:
        files (list): List of files with path and data.

    Returns:
        str: Formatted string of file contents.
    """
    contents = ""
    for file in files:
        file_path = file["path"]
        contents += f"\n**************** FILE: {file_path} ****************\n"
        contents += file["data"]
        contents += f"\n**************** EOF: {file_path} ****************\n"
    return contents


def get_files(startpath, ignore_patterns):
    """
    Retrieve files from the given starting path, ignoring specific patterns and binary files.

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
            and not is_binary_file(f)
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
            except UnicodeDecodeError as e:
                print(f"Error reading file {file_path}: {e}")
            except Exception as e:
                print(f"Unknown error reading file: {file_path}: {e}")
    return all_files


def parse_files(string, debug=False):
    """
    Parse files from a given string containing file delimiters and content.

    Args:
        string (str): The string containing the file delimiters and content.
        debug (bool): Flag to enable debug output.

    Returns:
        list: List of dictionaries containing filenames and contents.
    """
    matches = file_parse_pattern.findall(string)
    files = [
        {"filename": match[0].strip(), "contents": match[1].strip()}
        for match in matches
    ]
    
    if debug:
        print(f"Debug: parse_files found {len(files)} files")
        for file in files:
            print(f"Debug: Parsed file: {file['filename']}")
            print(f"Debug: Content preview: {file['contents'][:50]}...")
    
    return files


def is_in_middle_of_file(string):
    """
    Check if a given string is in the middle of a file based on start and end tokens.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string is in the middle of a file, False otherwise.
    """
    # Find all starting and closing tokens
    start_matches = middle_of_file_start_pattern.findall(string)
    end_matches = middle_of_file_end_pattern.findall(string)

    # Check if there's a start token without a corresponding end token
    if len(start_matches) > len(end_matches):
        return True
    return False


def extract_estimated_characters(string):
    """
    Extract the estimated character count from a given string.

    Args:
        string (str): The string containing the estimated character count.

    Returns:
        int: The extracted estimated character count.
    """
    pattern = re.compile(r"## ESTIMATED CHARACTERS:\n(\d+)")
    match = pattern.search(string)
    if match:
        return int(match.group(1))
    return 0


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
    """
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
        except Exception as e:
            print(f"Error writing file {file['filename']}:\n{e}")

    if debug:
        print(f"Debug: Finished writing {len(files)} files")
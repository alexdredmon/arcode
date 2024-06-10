import os
import re
from .gitignore_parser import is_ignored

from .constants import binary_extensions

file_parse_pattern = re.compile(
    r"===\.= ==== FILENAME: (?P<filename>.*?) = ===== =========\n```.*?\n(?P<content>.*?)\n```\n===\.= ==== EOF: (?P=filename) = ===== =========",
    re.DOTALL,
)
# Define the pattern for the starting token
middle_of_file_start_pattern = re.compile(
    r"===\.= ==== FILENAME: .*? = ===== =========\n```(.*?)\n", re.DOTALL
)
# Define the pattern for the closing token
middle_of_file_end_pattern = re.compile(
    r"===\.= ==== EOF: .*? = ===== =========\n", re.DOTALL
)

file_start_token = re.compile(
    r"===\.= ==== FILENAME: (.*?) = ===== =========", re.DOTALL
)

file_end_token = re.compile(
    r"===\.= ==== EOF: (.*?) = ===== =========", re.DOTALL
)


def extract_filename_start(text):
    matches = file_start_token.findall(text)
    if len(matches) == 1:
        return matches[0]
    else:
        return None


def extract_filename_end(text):
    matches = file_end_token.findall(text)
    if len(matches) == 1:
        return matches[0]
    else:
        return None


def is_binary_file(filename):
    return os.path.splitext(filename)[1].lower() in binary_extensions


def print_tree(startpath, ignore_patterns, prefix=""):
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
    contents = ""
    for file in files:
        file_path = file["path"]
        contents += f"\n**************** FILE: {file_path} ****************\n"
        contents += file["data"]
        contents += f"\n**************** EOF: {file_path} ****************\n"
    return contents


def get_files(startpath, ignore_patterns):
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


def parse_files(string):
    matches = file_parse_pattern.findall(string)
    files = [
        {"filename": match[0].strip(), "contents": match[1].strip()}
        for match in matches
    ]
    return files


def is_in_middle_of_file(string):
    # Find all starting and closing tokens
    start_matches = middle_of_file_start_pattern.findall(string)
    end_matches = middle_of_file_end_pattern.findall(string)

    # Check if there's a start token without a corresponding end token
    if len(start_matches) > len(end_matches):
        return True
    return False


def extract_estimated_characters(string):
    pattern = re.compile(r"## ESTIMATED CHARACTERS:\n(\d+)")
    match = pattern.search(string)
    if match:
        return int(match.group(1))
    return 0


def calculate_line_difference(filepath, new_content):
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

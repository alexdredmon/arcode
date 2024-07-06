import re

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
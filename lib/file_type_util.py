import os
import re
from .constants import binary_extensions, file_signatures

# Define the pattern for the starting token
file_start_token = re.compile(
    r"===\.= ==== FILENAME: (.*?) = ===== =========", re.DOTALL
)

# Define the pattern for the closing token
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

def get_mime_type(filename):
    """
    Determine the MIME type of a file based on its file signature.
    This function is cross-platform compatible.

    Args:
        filename (str): The filename to check.

    Returns:
        str: The MIME type of the file.
    """
    try:
        with open(filename, "rb") as file:
            file_signature = file.read(16)  # Read the first 16 bytes
    except IOError:
        return "application/octet-stream"  # Default to binary if file can't be read

    for mime_type, signatures in file_signatures.items():
        if any(
            file_signature.startswith(bytes.fromhex(sig)) for sig in signatures
        ):
            return mime_type

    # If no matching signature, try to detect text files
    try:
        with open(filename, "r", encoding="utf-8") as file:
            file.read(1024)  # Try reading as text
        return "text/plain"
    except UnicodeDecodeError:
        return "application/octet-stream"  # If can't be read as text, assume binary

def is_binary_file(filename):
    """
    Check if a given filename is a binary file based on its extension and MIME type.
    This function is cross-platform compatible.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    # Check extension first (fastest method)
    if os.path.splitext(filename)[1].lower() in binary_extensions:
        return True

    # If extension check doesn't determine, check MIME type
    mime_type = get_mime_type(filename)

    # List of MIME types that are considered text
    text_mime_types = [
        "text/plain",
        "text/html",
        "text/css",
        "text/xml",
        "application/json",
        "application/javascript",
        "application/xml",
        "application/xhtml+xml",
    ]

    if any(mime_type.startswith(text_type) for text_type in text_mime_types):
        return False

    # Consider all other types as binary
    return True
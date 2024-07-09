import base64
import os
import imghdr
import tiktoken

def process_image(image_path):
    """
    Process an image file and return its base64 encoded data URL.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded data URL of the image.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the file is not a recognized image format.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    image_type = imghdr.what(image_path)
    if not image_type:
        raise ValueError(f"Unrecognized image format: {image_path}")

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:image/{image_type};base64,{encoded_string}"

def calculate_image_token_cost(image_path, encoding):
    """
    Calculate the token cost of an image for a given encoding.

    Args:
        image_path (str): Path to the image file.
        encoding (tiktoken.Encoding): The encoding to use for token calculation.

    Returns:
        int: The number of tokens used by the image.
    """
    image_data = process_image(image_path)
    return len(encoding.encode(image_data))
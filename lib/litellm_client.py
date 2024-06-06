from litellm import completion
from config import API_KEY


def create_litellm_client():
    if not API_KEY:
        raise ValueError("API_KEY is not set")
    return completion

from litellm import completion
from litellm.llms.openai import OpenAIError
from config import OPENAI_API_KEY


def create_litellm_client():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")
    return completion
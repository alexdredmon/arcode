from litellm import completion
from config import get_api_keys

def create_litellm_client(model):
    # Just validate the model once, get API keys
    api_key = get_api_keys(model)

    return completion
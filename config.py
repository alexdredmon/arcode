import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_env_vars_from_config(config_vars, args=None):
    """
    Load environment variables from a given configuration.

    Args:
        config_vars (dict): A dictionary containing configuration variables.
        args (Namespace, optional): Additional arguments. Defaults to None.
    """
    for key, value in config_vars.items():
        os.environ[key] = value
    if args and 'resources' in config_vars:
        args.resources = config_vars['resources']

# Retrieve API keys based on model prefixes
def get_api_keys(model):
    """
    Retrieve API keys for different model providers.

    Args:
        model (str): The model prefix to determine the provider.

    Raises:
        ValueError: Throws an error if API keys are not set.

    Returns:
        str/tuple: The API key or a tuple with key, base, version depending on the provider.
    """
    if model.startswith("openai/"):
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set")
        return key
    elif model.startswith("anthropic/"):
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return key
    elif model.startswith("gemini/"):
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("GEMINI_API_KEY is not set")
        return key
    elif model.startswith("azure/"):
        key = os.getenv("AZURE_API_KEY", "")
        base = os.getenv("AZURE_API_BASE", "")
        version = os.getenv("AZURE_API_VERSION", "")
        if not key or not base or not version:
            raise ValueError("AZURE_API_KEY, AZURE_API_BASE, and AZURE_API_VERSION must be set")
        return (key, base, version)
    elif model.startswith("bedrock/"):
        key = os.getenv("AWS_ACCESS_KEY_ID", "")
        secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        region = os.getenv("AWS_REGION_NAME", "")
        if not key or not secret or not region:
            raise ValueError("AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION_NAME must be set")
        return (key, secret, region)
    else:
        raise ValueError(f"Unsupported model provider for model '{model}'")
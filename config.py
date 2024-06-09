import os
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

def load_env_vars_from_config(config_vars):
    for key, value in config_vars.items():
        os.environ[key] = value

# Retrieve API keys based on model prefixes
def get_api_keys(model):
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
    else:
        raise ValueError(f"Unsupported model provider for model '{model}'")

def load_env_vars_from_config(config_vars, args=None):
    for key, value in config_vars.items():
        os.environ[key] = value
    if args and 'resources' in config_vars:
        args.resources = config_vars['resources']

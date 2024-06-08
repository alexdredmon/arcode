import argparse
import os
import yaml
from config import get_api_keys, load_env_vars_from_config

ARG_KEYS = [
    "dir",
    "autowrite",
    "focused",
    "model",
    "model_embedding",
    "mode",
    "token_encoding",
    "ignore",
]

def parse_arguments():

    parser = argparse.ArgumentParser(description="arcode: AI driven development tool")
    parser.add_argument('--dir', type=str, default='.', help='The working directory of the codebase, default to current directory.')
    parser.add_argument('--autowrite', type=bool, default=False, help='Whether or not to immediately write the changeset.  Useful when piping to arcode, e.g. cat feature.txt | arcode')
    parser.add_argument('--focused', type=int, default=0, help='Enable focused mode to limit file context provided based on relevancy using embeddings - accepts an integer containing number of file chunks to limit context to.')
    parser.add_argument('--model', type=str, default='openai/gpt-4o', help='LLM provider/model to use with LiteLLM, default to openai/gpt-4o.')
    parser.add_argument('--model_embedding', type=str, default='openai/text-embedding-3-small', help='LLM provider/model to use for embeddings with LiteLLM, default to openai/text-embedding-3-small.')
    parser.add_argument('--mode', type=str, default='implement', choices=['implement', 'question'], help='Mode for the tool: "implement" for feature building and "question" for asking questions about the codebase.')
    parser.add_argument('--token_encoding', type=str, default='cl100k_base', help='Encoding used for counting tokens before issuing a completion request')
    parser.add_argument('--ignore', type=str, nargs='*', help='Additional ignore patterns to use when parsing .gitignore')
    parser.add_argument('requirements', nargs='*', type=str, help='Requirements for features to build on the codebase or question to ask about the codebase.')

    cli_args = parser.parse_args()

    # Load configuration from arcodeconf.yml if exists
    config_path = os.path.join(cli_args.dir, "arcodeconf.yml")

    cli_args.config_from_file = False
    if os.path.exists(config_path):
        cli_args.config_from_file = True
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            if config:
                config_args = config.get("args", {})
                if config_args:
                    for key in ARG_KEYS:
                        if key in config_args.keys():
                            setattr(cli_args, key, config_args.get(key))
                env_args = config_args.get("env", {})
                if env_args:
                    load_env_vars_from_config(env_args)
    return cli_args
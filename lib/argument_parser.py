import argparse
import os
import yaml
from config import load_env_vars_from_config

ARG_KEYS = [
    "dir",
    "auto-write",
    "focused",
    "model",
    "model-embedding",
    "mode",
    "ignore",
    "resources",
    "debug",
    "models",
    "maximum-estimated-cost",
    "max-file-size",
]


class ProvidedAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(
            namespace, f"{self.dest}_provided", True
        )  # Track if user provided


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="arcode: AI driven development tool"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="The working directory of the codebase, default to current directory.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--auto-write",
        type=bool,
        default=False,
        help="Whether or not to immediately write the changeset. Useful when piping to arcode, e.g. cat feature.txt | arcode",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--focused",
        type=int,
        default=0,
        help="Enable focused mode to limit file context provided based on relevancy using embeddings - accepts an integer containing number of file chunks to limit context to.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--model",
        type=str,
        default="openai/gpt-4o",
        help="LLM provider/model to use with LiteLLM, default to openai/gpt-4o.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--model-embedding",
        type=str,
        default="openai/text-embedding-3-small",
        help="LLM provider/model to use for embeddings with LiteLLM, default to openai/text-embedding-3-small.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="implement",
        choices=["implement", "question"],
        help='Mode for the tool: "implement" for feature building and "question" for asking questions about the codebase.',
        action=ProvidedAction,
    )
    parser.add_argument(
        "--ignore",
        type=str,
        nargs="*",
        help="Additional ignore patterns to use when parsing .gitignore",
        action=ProvidedAction,
    )
    parser.add_argument(
        "requirements",
        nargs="*",
        type=str,
        help="Requirements for features to build on the codebase or question to ask about the codebase.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--resources",
        nargs="*",
        type=str,
        help="List of URLs to fetch and include in the prompt context",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for additional output",
        default=False,
    )
    parser.add_argument(
        "--models",
        nargs="?",
        const=True,
        help="List available models. Optionally provide a filter string.",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--maximum-estimated-cost",
        type=float,
        default=5.0,
        help="Maximum estimated cost allowed. Actions with a larger estimated cost will not be allowed to execute. (integer or float with up to two decimal places)",
        action=ProvidedAction,
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=1000000,  # 1 MB default
        help="Maximum file size in bytes for files to be included in the prompt.",
        action=ProvidedAction,
    )

    # Set defaults for all custom provided flags
    for arg in ARG_KEYS:
        parser.set_defaults(**{f"{arg}_provided": False})

    cli_args = parser.parse_args()

    # Validate maximum-estimated-cost
    if cli_args.maximum_estimated_cost < 0 or round(cli_args.maximum_estimated_cost, 2) != cli_args.maximum_estimated_cost:
        parser.error("maximum-estimated-cost must be a non-negative number with at most two decimal places")

    # First check for the global configuration file
    global_config_path = os.path.expanduser("~/.config/arcodeconf.yml")

    # If the global config file exists, load it
    if os.path.exists(global_config_path):
        load_configurations(cli_args, global_config_path)

    # Load per-project configuration from arcodeconf.yml if it exists
    project_config_path = os.path.join(cli_args.dir, "arcodeconf.yml")
    if os.path.exists(project_config_path):
        load_configurations(cli_args, project_config_path)

    return cli_args


def load_configurations(cli_args, config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

        if config:
            config_args = config.get("args", {})
            if config_args:
                for key in ARG_KEYS:
                    # Convert kebab-case to snake_case for compatibility
                    snake_key = key.replace("-", "_")
                    # Only load config value if user has not provided it
                    if key in config_args and not getattr(
                        cli_args, f"{snake_key}_provided", False
                    ):
                        setattr(cli_args, snake_key, config_args.get(key))
                    elif snake_key in config_args and not getattr(
                        cli_args, f"{snake_key}_provided", False
                    ):
                        setattr(cli_args, snake_key, config_args.get(snake_key))

            env_args = config.get("env", {})
            if env_args:
                load_env_vars_from_config(env_args)

    return cli_args
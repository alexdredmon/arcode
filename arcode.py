#!/usr/bin/env python

import os
import sys
from InquirerPy import inquirer
from config import get_api_keys
from lib.argument_parser import parse_arguments
from lib.gitignore_parser import parse_gitignore
from lib.file_util import (
    print_tree,
    get_files,
    format_file_contents,
    parse_files,
    write_files,
)
from lib.litellm_client import create_litellm_client, calculate_token_count, get_available_models
from lib.status import print_configuration, print_tokens
from lib.streaming_response import stream_response
from lib.user_menu import handle_user_menu
from lib.shell_util import (
    LIGHT_ORANGE,
    LIGHT_PINK,
    LIGHT_BLUE,
    RESET_COLOR,
)
from lib.prompt_builder import build_prompt


def main():
    """
    Main entry point for the arcode application.
    Parse arguments, load necessary configurations, fetch files,
    print configurations, and handle user interactions.
    """
    args = parse_arguments()

    # Handle --help flag
    if '--help' in sys.argv:
        return

    # Handle --models flag
    if args.models is not None:
        filter_text = args.models if isinstance(args.models, str) else None
        available_models = get_available_models(filter_text)
        print(f"{LIGHT_ORANGE}Available models:{RESET_COLOR}")
        for model in available_models:
            print(f"- {model}")
        return

    # Get requirements
    if args.requirements:
        requirements = " ".join(args.requirements).strip()
    elif not sys.stdin.isatty():
        requirements = sys.stdin.read().strip()
    else:
        requirements = ""

    # Prompt for requirements if not provided
    if not requirements:
        print(f"{LIGHT_ORANGE} 🕹️  What are your requirements?")
        requirements = input(f"{LIGHT_PINK}    > {LIGHT_BLUE}")

    # Exit if still no requirements
    if not requirements:
        print(f"{LIGHT_ORANGE}No requirements provided. Exiting.{RESET_COLOR}")
        return

    # Store the requirements in args
    args.requirements = requirements

    # Parse gitignore
    ignore_patterns = parse_gitignore(
        os.path.join(args.dir, ".gitignore"), args.ignore
    )

    # Load API keys only if we have requirements
    try:
        get_api_keys(args.model)
    except ValueError as e:
        print(f"{LIGHT_ORANGE}Error: {e}{RESET_COLOR}")
        return

    startpath = args.dir

    print_configuration(args, requirements)

    user_content = build_prompt(
        args, requirements, startpath, ignore_patterns, []
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_content},
    ]

    client = create_litellm_client(args.model)

    try:
        input_tokens, output_tokens, total_tokens = calculate_token_count(
            args.model, messages
        )
        print_tokens(
            input_tokens, output_tokens, total_tokens, args.model
        )

        proceed = inquirer.confirm(
            message=f"  This will use ~{total_tokens:,} tokens before output - are you sure?",
            default=True,
        ).execute()

        if not proceed:
            print(f"\n 👋 {LIGHT_ORANGE}Good day!{RESET_COLOR}")
            return

        print(f"\n 🚀 {LIGHT_ORANGE}Let's do this.{RESET_COLOR}")

        answers = {"next_step": None}

        while answers["next_step"] != "🚪 Exit":
            files, streamed_response = stream_response(client, args, messages)
            answers = handle_user_menu(args, files, messages, streamed_response)

    except Exception as e:
        print(f"{LIGHT_ORANGE}An error occurred: {e}{RESET_COLOR}")
        return


if __name__ == "__main__":
    main()
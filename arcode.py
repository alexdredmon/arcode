#!/usr/bin/env python

import sys
from config import get_api_keys
from lib.argument_parser import parse_arguments
from lib.shell_util import (
    LIGHT_ORANGE,
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_RED,
    RESET_COLOR,
)

def initialize_core_imports():
    print(f"{LIGHT_BLUE} 🕰️  Initializing core imports...{RESET_COLOR}")
    global inquirer, get_multiline_input, get_available_models
    from InquirerPy import inquirer
    from lib.input_util import get_multiline_input
    from lib.litellm_client import get_available_models


def initialize_full_imports():
    print(f"{LIGHT_BLUE} 🕰️  Initializing full imports...{RESET_COLOR}")
    global tiktoken, stream_response, handle_user_menu, build_prompt
    global create_litellm_client, calculate_token_count
    global initialize_token_counter, get_token_counts, add_initial_image_tokens, add_image_tokens, print_token_counts
    global check_cost_exceeds_maximum, print_configuration, print_tokens, calculate_image_token_cost

    print(f"{LIGHT_BLUE} 🕰️  Loading tiktoken...{RESET_COLOR}")
    import tiktoken

    print(f"{LIGHT_BLUE} 🕰️  Loading stream_response...{RESET_COLOR}")
    from lib.streaming_response import stream_response

    print(f"{LIGHT_BLUE} 🕰️  Loading handle_user_menu...{RESET_COLOR}")
    from lib.user_menu import handle_user_menu

    print(f"{LIGHT_BLUE} 🕰️  Loading prompt_builder...{RESET_COLOR}")
    from lib.prompt_builder import build_prompt

    print(f"{LIGHT_BLUE} 🕰️  Loading litellm_client...{RESET_COLOR}")
    from lib.litellm_client import create_litellm_client, calculate_token_count

    print(f"{LIGHT_BLUE} 🕰️  Loading token_counter...{RESET_COLOR}")
    from lib.token_counter import (
        initialize_token_counter,
        get_token_counts,
        add_initial_image_tokens,
        add_image_tokens,
        print_token_counts,
    )

    print(f"{LIGHT_BLUE} 🕰️  Loading status...{RESET_COLOR}")
    from lib.status import (
        check_cost_exceeds_maximum,
        print_configuration,
        print_tokens,
    )

    print(f"{LIGHT_BLUE} 🕰️  Loading image_util...{RESET_COLOR}")
    from lib.image_util import calculate_image_token_cost


def initialize_encoding(args):
    print(f"{LIGHT_BLUE} 🕰️  Initializing encodings...{RESET_COLOR}")
    try:
        encoding = tiktoken.encoding_for_model(args.model.split("/")[-1])
    except Exception as e:
        print(
            f"{LIGHT_BLUE} 💁‍♀️ Defaulting to 'cl100k_base' - no model-specific encoding for {args.model}.{RESET_COLOR}"
        )
        encoding = tiktoken.get_encoding("cl100k_base")
    args.encoding = encoding


def handle_models_flag(args):
    initialize_core_imports()
    filter_text = args.models if isinstance(args.models, str) else None
    available_models = get_available_models(filter_text)
    print(f"{LIGHT_ORANGE}Available models:{RESET_COLOR}")
    for model in available_models:
        print(f"- {model}")
    return True


def get_requirements(args):
    initialize_core_imports()
    if args.requirements:
        return " ".join(args.requirements).strip()
    elif not sys.stdin.isatty():
        return sys.stdin.read().strip()
    else:
        print(f"\n{LIGHT_ORANGE} 🕹️  What are your requirements?")
        return get_multiline_input("    > ")


def process_requirements(args, requirements):
    initialize_full_imports()
    initialize_encoding(args)

    # Store the requirements in args and initialize requirements_history
    args.requirements = requirements
    args.requirements_history = [requirements]

    # Load API keys only if we have requirements
    try:
        get_api_keys(args.model)
    except ValueError as error:
        print(f"{LIGHT_ORANGE}Error: {error}{RESET_COLOR}")
        return

    print("")
    # Print configuration
    print_configuration(args, requirements)

    # Initialize the token counter
    initialize_token_counter(args.model)
    print("")

    user_content = build_prompt(args, requirements, [])

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": format_content_for_litellm(user_content)},
    ]

    client = create_litellm_client(args.model)

    # Calculate image token costs and add to initial count
    if args.images:
        print(f"\n{LIGHT_ORANGE} 🖼️  IMAGES: {RESET_COLOR}")
        total_image_tokens = 0
        for image_path in args.images:
            image_tokens = calculate_image_token_cost(
                image_path, args.encoding
            )
            total_image_tokens += image_tokens
            print(
                f"    {LIGHT_PINK}* {LIGHT_BLUE}{image_path} {LIGHT_ORANGE}({image_tokens:,} tokens){RESET_COLOR}"
            )
        add_initial_image_tokens(args.images)
        print(
            f"    {LIGHT_PINK}Total image tokens: {LIGHT_BLUE}{total_image_tokens:,}{RESET_COLOR}"
        )

    try:
        token_counts = get_token_counts(messages)
        total_cost = print_token_counts()

        if check_cost_exceeds_maximum(total_cost, args.max_estimated_cost):
            print(
                f"{LIGHT_RED}Operation cancelled due to exceeding cost limit.{RESET_COLOR}"
            )
            return

        proceed = inquirer.confirm(
            message=f"  This will use ~{token_counts['total_tokens']:,} tokens before output - are you sure?",
            default=True,
        ).execute()

        if not proceed:
            print(f"\n 👋 {LIGHT_ORANGE}Good day!{RESET_COLOR}")
            return

        print(f"\n 🚀 {LIGHT_ORANGE}Let's do this.{RESET_COLOR}")

        answers = {"next_step": None}

        while answers["next_step"] != "🚪 Exit":
            files, streamed_response = stream_response(client, args, messages)
            answers = handle_user_menu(
                args, files, messages, streamed_response
            )

            # If there's a followup prompt, add it to the requirements_history
            if answers["next_step"] == "💬 Followup prompt":
                args.requirements_history.append(messages[-1]["content"])

    except Exception as error:
        print(f"{LIGHT_ORANGE}An error occurred: {error}{RESET_COLOR}")
        return


def format_content_for_litellm(content):
    """
    Format the content returned by build_prompt for LiteLLM.

    Args:
        content (list): List of content items returned by build_prompt.

    Returns:
        list: Formatted content for LiteLLM.
    """
    print(f"{LIGHT_BLUE} 🕰️  Formatting content for LiteLLM...{RESET_COLOR}")
    formatted_content = []
    for item in content:
        if item["type"] == "text":
            formatted_content.append({"type": "text", "text": item["text"]})
        elif item["type"] == "image_url":
            formatted_content.append(
                {"type": "image_url", "image_url": item["image_url"]}
            )
    return formatted_content


def main():
    """
    Main entry point for the arcode application.
    Parse arguments, load necessary configurations, fetch files,
    print configurations, and handle user interactions.
    """
    args = parse_arguments()

    # Handle --models flag
    if args.models is not None:
        return handle_models_flag(args)

    # Get requirements
    requirements = get_requirements(args)

    # Exit if no requirements
    if not requirements:
        print(f"{LIGHT_ORANGE}No requirements provided. Exiting.{RESET_COLOR}")
        return

    print("")
    # Process requirements
    process_requirements(args, requirements)


if __name__ == "__main__":
    main()
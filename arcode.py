#!/usr/bin/env python

import sys
import tiktoken

from InquirerPy import inquirer
from config import get_api_keys
from lib.argument_parser import parse_arguments
from lib.litellm_client import (
    create_litellm_client,
    calculate_token_count,
    get_available_models,
)
from lib.status import check_cost_exceeds_maximum, print_configuration, print_tokens
from lib.streaming_response import stream_response
from lib.user_menu import handle_user_menu
from lib.shell_util import (
    LIGHT_ORANGE,
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_RED,
    RESET_COLOR,
)
from lib.prompt_builder import build_prompt
from lib.image_util import calculate_image_token_cost
from lib.token_counter import initialize_token_counter, get_token_counts, add_initial_image_tokens, add_image_tokens, print_token_counts
from lib.input_util import get_multiline_input

def main():
    """
    Main entry point for the arcode application.
    Parse arguments, load necessary configurations, fetch files,
    print configurations, and handle user interactions.
    """
    args = parse_arguments()

    # Handle --help flag
    if "--help" in sys.argv:
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
        requirements = get_multiline_input("    > ")

    # Exit if still no requirements
    if not requirements:
        print(f"{LIGHT_ORANGE}No requirements provided. Exiting.{RESET_COLOR}")
        return

    # Store the requirements in args and initialize requirements_history
    args.requirements = requirements
    args.requirements_history = [requirements]

    # Load API keys only if we have requirements
    try:
        get_api_keys(args.model)
    except ValueError as error:
        print(f"{LIGHT_ORANGE}Error: {error}{RESET_COLOR}")
        return

    # Initialize encoding before print_configuration
    try:
        encoding = tiktoken.encoding_for_model(args.model.split("/")[-1])
    except Exception as e:
        print(f"{LIGHT_BLUE} ⚠️  No model-specific encoding for "
              f"{args.model}, defaulting to 'cl100k_base'.{RESET_COLOR}")
        encoding = tiktoken.get_encoding("cl100k_base")
    args.encoding = encoding

    # Print configuration only once
    print_configuration(args, requirements)

    # Initialize the token counter
    initialize_token_counter(args.model)

    user_content = build_prompt(args, requirements, [])

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": format_content_for_litellm(user_content)}
    ]

    client = create_litellm_client(args.model)

    # Calculate image token costs and add to initial count
    if args.images:
        print(f"\n{LIGHT_ORANGE} 🖼️  IMAGES: {RESET_COLOR}")
        total_image_tokens = 0
        for image_path in args.images:
            image_tokens = calculate_image_token_cost(image_path, encoding)
            total_image_tokens += image_tokens
            print(f"    {LIGHT_PINK}* {LIGHT_BLUE}{image_path} {LIGHT_ORANGE}({image_tokens:,} tokens){RESET_COLOR}")
        add_initial_image_tokens(args.images)
        print(f"    {LIGHT_PINK}Total image tokens: {LIGHT_BLUE}{total_image_tokens:,}{RESET_COLOR}")

    try:
        token_counts = get_token_counts(messages)
        total_cost = print_token_counts()

        if check_cost_exceeds_maximum(total_cost, args.max_estimated_cost):
            print(f"{LIGHT_RED}Operation cancelled due to exceeding cost limit.{RESET_COLOR}")
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
    formatted_content = []
    for item in content:
        if item["type"] == "text":
            formatted_content.append({"type": "text", "text": item["text"]})
        elif item["type"] == "image_url":
            formatted_content.append({"type": "image_url", "image_url": item["image_url"]})
    return formatted_content

if __name__ == "__main__":
    main()
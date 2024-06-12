#!/usr/bin/env python

import os
import sys
import io
import requests
from contextlib import redirect_stdout
from bs4 import BeautifulSoup
from InquirerPy import inquirer
import pyperclip
from litellm.llms.openai import OpenAIError
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from config import get_api_keys
from lib.argument_parser import parse_arguments
from lib.gitignore_parser import parse_gitignore
from lib.file_util import (
    extract_filename_start,
    extract_filename_end,
    is_in_middle_of_file,
    print_tree,
    get_files,
    format_file_contents,
    is_binary_file,
    is_ignored,
    parse_files,
    extract_estimated_characters,
    calculate_line_difference,
    write_files,  # Updated reference
)
from lib.prompt_templates import (
    AUTODEV_PROMPT_PRE,
    AUTODEV_PROMPT_POST_TEMPLATE,
    QUESTION_PROMPT_PRE,
    QUESTION_PROMPT_POST_TEMPLATE,
)
from lib.litellm_client import create_litellm_client, calculate_token_count
from lib.status import print_configuration, print_tokens
from lib.streaming_response import stream_response
from lib.user_menu import handle_user_menu
from lib.embedding_util import get_top_relevant_files
from lib.shell_util import (
    LIGHT_PINK,
    LIGHT_BLUE,
    WHITE_ON_BLACK,
    BLACK_ON_WHITE,
    RESET_COLOR,
)
from lib.prompt_builder import (
    build_prompt,
)  # New import for prompt building logic


def main():
    """
    Main entry point for the arcode application.
    Parse arguments, load necessary configurations, fetch files,
    print configurations, and handle user interactions.
    """
    args = parse_arguments()

    if not args.requirements:
        if sys.stdin.isatty():
            requirements = " ".join(args.requirements)
        else:
            requirements = sys.stdin.read().strip()
    else:
        requirements = " ".join(args.requirements).strip()

    ignore_patterns = parse_gitignore(
        os.path.join(args.dir, ".gitignore"), args.ignore
    )

    api_keys = get_api_keys(args.model)

    startpath = args.dir

    print_configuration(args, requirements)

    # Use the build_prompt function to replace the in-place `redirect_stdout` logic
    user_content = build_prompt(
        args, requirements, startpath, ignore_patterns, []
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_content},
    ]

    client = create_litellm_client(args.model)

    input_tokens, output_tokens, total_tokens = calculate_token_count(
        args.model, messages, args.token_encoding
    )
    print_tokens(
        input_tokens, output_tokens, total_tokens, args.token_encoding
    )

    proceed = inquirer.confirm(
        message=f"This will use ~{total_tokens:,} before output - are you sure?",
        default=True,
    ).execute()

    if not proceed:
        exit("\n👋 Good day!")
    else:
        print("\n🚀 Let's do this.")

    answers = {"next_step": None}

    while answers["next_step"] != "🚪 Exit":
        files, streamed_response = stream_response(client, args, messages)
        answers = handle_user_menu(args, files, messages, streamed_response)


if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import sys
import io
from contextlib import redirect_stdout
from InquirerPy import prompt
import pyperclip

from config import API_KEY
from lib.argument_parser import parse_arguments
from lib.gitignore_parser import parse_gitignore
from lib.file_util import print_tree, print_file_contents, is_binary_file, is_ignored, parse_files, extract_estimated_characters
from lib.openai_client import create_openai_client, AUTODEV_PROMPT_PRE, AUTODEV_PROMPT_POST_TEMPLATE, LIGHT_PINK, LIGHT_GREEN, RESET_COLOR


def main():
    args = parse_arguments()

    if sys.stdin.isatty():
        requirements = ' '.join(args.requirements)
    else:
        requirements = sys.stdin.read().strip()

    ignore_patterns = parse_gitignore(os.path.join(args.dir, '.gitignore'))

    f = io.StringIO()
    with redirect_stdout(f):
        print(AUTODEV_PROMPT_PRE)

        startpath = args.dir

        print("Directory Tree:")
        print_tree(startpath, ignore_patterns)

        print("\nFile Contents:")
        print_file_contents(startpath, ignore_patterns)

        autodev_prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(requirements=requirements)
        print(autodev_prompt_post)

    USER_CONTENT = f.getvalue()

    # Ensure the API key is set
    if not API_KEY:
        raise ValueError("API_KEY is not set")

    print(f"{LIGHT_GREEN}Building feature(s):\n{requirements}{RESET_COLOR}")

    client = create_openai_client(API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_CONTENT}
        ],
        stream=True
    )

    print(f"{LIGHT_GREEN}Streaming response:{RESET_COLOR}")
    streamed_response = ""
    response_chunks = []

    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content is not None:
            print(f"{LIGHT_PINK}{delta.content}{RESET_COLOR}", end="", flush=True)
            streamed_response += delta.content
            response_chunks.append(delta.content)

    choices = ['Copy full response']
    files = parse_files(streamed_response)
    for file in files:
        filename = file["filename"]
        choices.append(f"Copy file {filename}")

    choices.append("Exit")

    answers = {
        "next_step": None
    }
    questions = [
        {
            'type': 'list',
            'name': 'next_step',
            'message': 'What would you like to do next?',
            'choices': choices,
        }
    ]

    while answers["next_step"] != "Exit":
        answers = prompt(questions)

        if answers['next_step'] == 'Copy full response':
            pyperclip.copy(streamed_response)
            print("Response copied to clipboard.")

        if answers['next_step'].startswith("Copy file "):
            for file in files:
                filename = file["filename"]
                if answers['next_step'] == f"Copy file {filename}":
                    pyperclip.copy(file["contents"])

if __name__ == "__main__":
    main()

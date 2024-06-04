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
from lib.file_util import print_tree, get_files, format_file_contents, is_binary_file, is_ignored, parse_files, extract_estimated_characters, calculate_line_difference
from lib.openai_client import create_openai_client, AUTODEV_PROMPT_PRE, AUTODEV_PROMPT_POST_TEMPLATE
from lib.shell_util import (
    LIGHT_PINK, LIGHT_GREEN, LIGHT_RED, LIGHT_BLUE, RESET_COLOR, WHITE_ON_DARK_BLUE, BLACK_ON_WHITE,
    WHITE_ON_BLACK, LIGHT_ORANGE, BLACK_BACKGROUND
)
from lib.file_writer import write_files

from lib.embedding_util import get_top_relevant_files

def main():
    args = parse_arguments()

    if sys.stdin.isatty():
        requirements = ' '.join(args.requirements)
    else:
        requirements = sys.stdin.read().strip()

    ignore_patterns = parse_gitignore(os.path.join(args.dir, '.gitignore'))

    if not API_KEY:
        raise ValueError("API_KEY is not set")

    file_contents = None
    startpath = args.dir

    if args.focused:
        files = get_top_relevant_files(
            startpath=startpath,
            ignore_patterns=ignore_patterns,
            query=requirements,
            num_files=args.focused,
        )
        print(f"\n{WHITE_ON_BLACK} 🔬 {BLACK_ON_WHITE} FOCUSING ON {args.focused} MOST RELAVENT FILES: {RESET_COLOR}")
        for file in files:
            path = file["path"]
            score = round(file["score"], 2)
            print(f" - {LIGHT_BLUE}{path} {LIGHT_GREEN}({score}){RESET_COLOR}")
    else:
        files = get_files(startpath, ignore_patterns)

    f = io.StringIO()
    with redirect_stdout(f):
        print(AUTODEV_PROMPT_PRE)

        print("Directory Tree:")
        print_tree(startpath, ignore_patterns)

        print("\nFile Contents:")
        print(format_file_contents(files))

        autodev_prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(requirements=requirements)
        print(autodev_prompt_post)
        
        USER_CONTENT = f.getvalue()

    print(f"\n{WHITE_ON_BLACK} 🏗️  {BLACK_ON_WHITE} BUILDING FEATURE(S): {RESET_COLOR}\n{LIGHT_BLUE}{requirements}{RESET_COLOR}")

    client = create_openai_client(API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_CONTENT}
        ],
        stream=True
    )

    print(f"\n{WHITE_ON_BLACK} 🌐 {BLACK_ON_WHITE} STREAMING RESPONSE: {RESET_COLOR}")
    streamed_response = ""
    response_chunks = []

    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content is not None:
            print(f"{BLACK_BACKGROUND}{LIGHT_ORANGE}{delta.content}{RESET_COLOR}", end="", flush=True)
            streamed_response += delta.content
            response_chunks.append(delta.content)

    files = parse_files(streamed_response)
    if sys.stdin.isatty():
        choices = ['Write changeset to files', 'Copy full response']
        for file in files:
            filename = file["filename"]
            choices.append(f"Copy file {filename}")

        # Print file changes
        for file in files:
            filename = file["filename"]
            new_content = file["contents"]
            line_diff = calculate_line_difference(os.path.join(args.dir, filename), new_content)
            line_diff_str = f"{LIGHT_GREEN}{filename} ({line_diff:+d}){RESET_COLOR}"
            print(f"\n\n{WHITE_ON_BLACK} 📁 {BLACK_ON_WHITE} FILES TO UPDATE: {RESET_COLOR}")
            print(line_diff_str)
            print("")

        choices.append("Exit")

        answers = {
            "next_step": None
        }
        questions = [
            {
                'type': 'list',
                'name': 'next_step',
                'message': '↕',
                'choices': choices,
            }
        ]

        print(f"{WHITE_ON_BLACK} ⚡️ {BLACK_ON_WHITE} ACTION: {RESET_COLOR}")
        while answers["next_step"] != "Exit":
            answers = prompt(questions)

            if answers['next_step'] == 'Copy full response':
                pyperclip.copy(streamed_response)
                print("Response copied to clipboard.")

            elif answers['next_step'].startswith("Copy file "):
                for file in files:
                    filename = file["filename"]
                    if answers['next_step'] == f"Copy file {filename}":
                        pyperclip.copy(file["contents"])

            elif answers['next_step'] == 'Write changeset to files':
                write_files(files, args.dir)
                print(f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}")
    else:
        write_files(files, args.dir)
        print(f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}")

if __name__ == "__main__":
    main()
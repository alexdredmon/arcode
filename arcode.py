#!/usr/bin/env python

import os
import sys
import io

from contextlib import redirect_stdout
from InquirerPy import prompt
import pyperclip
from litellm.llms.openai import OpenAIError

from config import get_api_keys
from lib.argument_parser import parse_arguments
from lib.gitignore_parser import parse_gitignore
from lib.file_util import print_tree, get_files, format_file_contents, is_binary_file, is_ignored, parse_files, extract_estimated_characters, calculate_line_difference
from lib.prompt_templates import AUTODEV_PROMPT_PRE, AUTODEV_PROMPT_POST_TEMPLATE, QUESTION_PROMPT_PRE, QUESTION_PROMPT_POST_TEMPLATE
from lib.litellm_client import create_litellm_client, calculate_token_count
from lib.shell_util import (
    LIGHT_PINK, LIGHT_GREEN, LIGHT_RED, LIGHT_BLUE, RESET_COLOR, WHITE_ON_DARK_BLUE, BLACK_ON_WHITE,
    WHITE_ON_BLACK, LIGHT_ORANGE, BLACK_BACKGROUND
)
from lib.file_writer import write_files

from lib.embedding_util import get_top_relevant_files

def main():
    args = parse_arguments()

    if not args.requirements:
        if sys.stdin.isatty():
            requirements = ' '.join(args.requirements)
        else:
            requirements = sys.stdin.read().strip()
    else:
        requirements = ' '.join(args.requirements).strip()

    ignore_patterns = parse_gitignore(os.path.join(args.dir, '.gitignore'))

    print(f"\n{WHITE_ON_BLACK} ⚙️ {BLACK_ON_WHITE} CONFIGURATION: {RESET_COLOR}")
    print(f"{LIGHT_PINK}       Config file: {LIGHT_BLUE}{args.config_from_file}{RESET_COLOR}")
    print(f"{LIGHT_PINK}         Directory: {LIGHT_BLUE}{args.dir}{RESET_COLOR}")
    print(f"{LIGHT_PINK}             Model: {LIGHT_BLUE}{args.model}{RESET_COLOR}")
    print(f"{LIGHT_PINK}   Embedding Model: {LIGHT_BLUE}{args.model_embedding}{RESET_COLOR}")
    print(f"{LIGHT_PINK}        Auto-write: {LIGHT_BLUE}{args.autowrite}{RESET_COLOR}")
    print(f"{LIGHT_PINK}           Focused: {LIGHT_BLUE}{args.focused}{RESET_COLOR}")
    print(f"{LIGHT_PINK}              Mode: {LIGHT_BLUE}{args.mode}{RESET_COLOR}")

    # Validate and fetch the API keys for the provided model
    api_keys = get_api_keys(args.model)

    file_contents = None
    startpath = args.dir

    if args.focused:
        files = get_top_relevant_files(
            startpath=startpath,
            ignore_patterns=ignore_patterns,
            query=requirements,
            num_files=args.focused,
            # model=args.model,
            model_embedding=args.model_embedding
        )
        print(f"\n{WHITE_ON_BLACK} 🔬 {BLACK_ON_WHITE} FOCUSING ON {args.focused} MOST RELEVANT FILES: {RESET_COLOR}")
        for file in files:
            path = file["path"]
            score = round(file["score"], 2)
            score_viz = '[' + (int(score * 10) * '🟩') + ((10 - int(score * 10)) * '⬛️') + ']'
            print(f" - {score_viz} {LIGHT_BLUE}{path} {LIGHT_GREEN}({score}){RESET_COLOR}")
    else:
        files = get_files(startpath, ignore_patterns)

    f = io.StringIO()
    with redirect_stdout(f):
        if args.mode == "question":
            print(QUESTION_PROMPT_PRE)
        else:
            print(AUTODEV_PROMPT_PRE)

        print("Directory Tree:")
        print_tree(startpath, ignore_patterns)

        print("\nFile Contents:")
        print(format_file_contents(files))

        if args.mode == "question":
            prompt_post = QUESTION_PROMPT_POST_TEMPLATE.format(requirements=requirements)
        else:
            prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(requirements=requirements)

        print(prompt_post)

        USER_CONTENT = f.getvalue()

    print(f"\n{WHITE_ON_BLACK} 🏗️  {BLACK_ON_WHITE} BUILDING FEATURE(S): {RESET_COLOR}\n{LIGHT_BLUE}{requirements}{RESET_COLOR}")

    answers = {
        "next_step": None
    }
    messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": USER_CONTENT}]

    client = create_litellm_client(args.model)

    # Calculate and print token count using tiktoken
    total_token_count = calculate_token_count(args.model, messages, args.token_encoding)
    print(f"\n{WHITE_ON_BLACK} 🔢 {BLACK_ON_WHITE} TOTAL TOKEN COUNT: {RESET_COLOR} {total_token_count}\n")

    while answers["next_step"] != "🚪 Exit":
        try:
            completion = client(model=args.model, messages=messages, stream=True)

            print(f"\n{WHITE_ON_BLACK} 🌐 {BLACK_ON_WHITE} STREAMING RESPONSE: {RESET_COLOR}")
            streamed_response = ""
            response_chunks = []

            for chunk in completion:
                if chunk and chunk.choices and chunk.choices[0] and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if delta.get('content'):
                        print(f"{BLACK_BACKGROUND}{LIGHT_ORANGE}{delta['content']}{RESET_COLOR}", end="", flush=True)
                        streamed_response += delta['content']
                        response_chunks.append(delta['content'])

        except OpenAIError as e:
            print(f"{BLACK_BACKGROUND}{LIGHT_RED}{e.message}{RESET_COLOR}")
            break

        files = parse_files(streamed_response)
        if sys.stdin.isatty():
            choices = ['💬 Followup prompt', '🏗️  Write changeset to files', '📑 Copy full response']
            for file in files:
                filename = file["filename"]
                choices.append(f"📄 Copy file {filename}")

            # Print file changes
            for file in files:
                filename = file["filename"]
                new_content = file["contents"]
                line_diff = calculate_line_difference(os.path.join(args.dir, filename), new_content)
                line_diff_str = f"{LIGHT_GREEN}{filename} ({line_diff:+d}){RESET_COLOR}"
                print(f"\n\n{WHITE_ON_BLACK} 📁 {BLACK_ON_WHITE} FILES TO UPDATE: {RESET_COLOR}")
                print(line_diff_str)
                print("")

            choices.append("🚪 Exit")
            if args.mode == "question":
                choices = ["🚪 Exit"]

            questions = [
                {
                    'type': 'list',
                    'name': 'next_step',
                    'message': '↕',
                    'choices': choices,
                }
            ]

            print(f"{WHITE_ON_BLACK} ⚡️ {BLACK_ON_WHITE} ACTION: {RESET_COLOR}")
            exit_menu = False
            if args.autowrite:
                write_files(files, args.dir)
                print(f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}")

            while not exit_menu:
                answers = prompt(questions)
                if answers['next_step'] == '📑 Copy full response':
                    pyperclip.copy(streamed_response)
                    print("Response copied to clipboard.")
                elif answers['next_step'].startsWith("📄 Copy file "):
                    for file in files:
                        filename = file["filename"]
                        if answers['next_step'] == f"📄 Copy file {filename}":
                            pyperclip.copy(file["contents"])
                elif answers['next_step'] == '🏗️  Write changeset to files':
                    write_files(files, args.dir)
                    print(f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}")
                elif answers['next_step'] == "💬 Followup prompt":
                    followup = input(">")
                    messages.append({"role": "assistant", "content": streamed_response})
                    messages.append({"role": "user", "content": followup})
                    exit_menu = True
                elif answers['next_step'] == "🚪 Exit":
                    exit_menu = True
    else:
        if args.autowrite:
            write_files(files, args.dir)
            print(f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}")

if __name__ == "__main__":
    main()
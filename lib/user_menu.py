from InquirerPy import prompt
import pyperclip
import os
from lib.file_io import (
    calculate_line_difference,
    write_files,
)
from lib.file_parser import (
    format_file_contents,
)
from lib.shell_util import (
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_GREEN,
    LIGHT_ORANGE,
    RESET_COLOR,
)
from lib.token_counter import get_token_counts, print_token_counts
import sys


def handle_user_menu(args, files, messages, streamed_response):
    answers = {"next_step": None}

    if sys.stdin.isatty():
        choices = [
            "💬 Followup prompt",
            "🏗️  Write changeset to files",
            "📑 Copy full response",
        ]

        for file in files:
            filename = file["filename"]
            choices.append(f"📄 Copy file {filename}")

        if len(files):
            print(f"\n\n{LIGHT_ORANGE} 📃 REQUIREMENTS: {RESET_COLOR}")
            for i, req in enumerate(args.requirements_history):
                if i > 0:
                    print("")
                print(f"{LIGHT_PINK}    > {LIGHT_BLUE}{req}{RESET_COLOR}")

            print(f"\n\n{LIGHT_ORANGE} 📁 FILES TO UPDATE: {RESET_COLOR}")

        # Print file changes
        for file in files:
            filename = file["filename"]
            new_content = file["contents"]
            line_diff = calculate_line_difference(
                os.path.join(args.dir, filename), new_content
            )
            line_diff_str = f"    {LIGHT_PINK}* {LIGHT_GREEN}{filename} ({line_diff:+d}){RESET_COLOR}"
            print(line_diff_str)

        choices.append("🚪 Exit")
        if args.mode == "question":
            choices = ["🚪 Exit"]

        questions = [
            {
                "type": "list",
                "name": "next_step",
                "message": "↕",
                "choices": choices,
            }
        ]

        get_token_counts(messages)
        print_token_counts()
        print(f"{LIGHT_ORANGE} ⚡️ ACTION: {RESET_COLOR}")
        exit_menu = False
        if args.auto_write:
            write_files(files, args.dir)
            print(f"\n{LIGHT_ORANGE} ✅ CHANGESET WRITTEN {RESET_COLOR}")

        while not exit_menu:
            answers = prompt(questions)
            if answers["next_step"] == "📑 Copy full response":
                pyperclip.copy(streamed_response)
                print("Response copied to clipboard.")
            elif answers["next_step"].startswith("📄 Copy file "):
                for file in files:
                    filename = file["filename"]
                    if answers["next_step"] == f"📄 Copy file {filename}":
                        pyperclip.copy(file["contents"])
            elif answers["next_step"] == "🏗️  Write changeset to files":
                write_files(files, args.dir)
                print(f"\n{LIGHT_ORANGE} ✅ CHANGESET WRITTEN {RESET_COLOR}")
            elif answers["next_step"] == "💬 Followup prompt":
                followup = input(f"     {LIGHT_PINK}> {LIGHT_BLUE}")
                messages.append({"role": "user", "content": followup})
                exit_menu = True
            elif answers["next_step"] == "🚪 Exit":
                exit_menu = True

    else:
        if args.auto_write:
            write_files(files, args.dir)
            print(f"\n{LIGHT_ORANGE} ✅ CHANGESET WRITTEN {RESET_COLOR}")

    return answers
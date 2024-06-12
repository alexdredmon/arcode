from InquirerPy import prompt
import pyperclip
import os
from lib.file_util import (
    calculate_line_difference,
    write_files,
)
from lib.litellm_client import calculate_token_count
from lib.shell_util import (
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_GREEN,
    WHITE_ON_BLACK,
    BLACK_ON_WHITE,
    RESET_COLOR,
)
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
            requirements_text = " ".join(args.requirements)
            print(
                f"\n\n{WHITE_ON_BLACK} 📃 {BLACK_ON_WHITE} REQUIREMENTS: {RESET_COLOR}\n{LIGHT_PINK}    > {LIGHT_BLUE}{requirements_text}{RESET_COLOR}"
            )
            print(
                f"\n\n{WHITE_ON_BLACK} 📁 {BLACK_ON_WHITE} FILES TO UPDATE: {RESET_COLOR}"
            )

        # Print file changes
        for file in files:
            filename = file["filename"]
            new_content = file["contents"]
            line_diff = calculate_line_difference(
                os.path.join(args.dir, filename), new_content
            )
            line_diff_str = f"    {LIGHT_PINK}* {LIGHT_GREEN}{filename} ({line_diff:+d}){RESET_COLOR}"
            print(line_diff_str)
            print("")

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

        input_tokens, output_tokens, total_tokens = calculate_token_count(
            args.model, messages, args.token_encoding
        )
        print(
            f"""
{WHITE_ON_BLACK} 🧮 {BLACK_ON_WHITE} TOKENS ({total_tokens:,} total) [{args.token_encoding}]{RESET_COLOR}
    {LIGHT_PINK}In: {LIGHT_BLUE}{input_tokens:,}{RESET_COLOR}
    {LIGHT_PINK}Out: {LIGHT_BLUE}{output_tokens:,}{RESET_COLOR}
                """
        )

        print(f"{WHITE_ON_BLACK} ⚡️ {BLACK_ON_WHITE} ACTION: {RESET_COLOR}")
        exit_menu = False
        if args.autowrite:
            write_files(files, args.dir)
            print(
                f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}"
            )

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
                print(
                    f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}"
                )
            elif answers["next_step"] == "💬 Followup prompt":
                followup = input(">")
                messages.append({"role": "user", "content": followup})
                exit_menu = True
            elif answers["next_step"] == "🚪 Exit":
                exit_menu = True

    else:
        if args.autowrite:
            write_files(files, args.dir)
            print(
                f"\n{WHITE_ON_BLACK} ✅ {BLACK_ON_WHITE} CHANGESET WRITTEN {RESET_COLOR}"
            )

    return answers

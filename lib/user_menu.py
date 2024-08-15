from InquirerPy import prompt
import pyperclip
import os
import subprocess
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
from lib.prompt_builder import reload_files
import sys


def display_token_count_and_cost(messages):
    """
    Display token count and cost estimate.
    """
    get_token_counts(messages)
    return print_token_counts()


def run_script(file_path):
    """
    Run a .sh or .py script.

    Args:
        file_path (str): The path to the script file.
    """
    if file_path.endswith(".sh"):
        subprocess.run(["chmod", "+x", file_path])
        subprocess.run(["/bin/bash", file_path])
    elif file_path.endswith(".py"):
        subprocess.run(["python", file_path])


def handle_user_menu(args, files, messages, streamed_response):
    answers = {"next_step": None}

    if sys.stdin.isatty():
        files_written = False
        while True:
            choices = [
                "💬 Followup prompt",
                "🏗️  Write changeset to files",
                "🔄 Reload files",
                "📑 Copy full response",
            ]

            for file in files:
                filename = file["filename"]
                choices.append(f"📄 Copy file {filename}")

            # Display token count and cost estimate only once
            display_token_count_and_cost(messages)

            if len(files):
                print(f"{LIGHT_ORANGE} 📃 REQUIREMENTS: {RESET_COLOR}")
                for i, req in enumerate(args.requirements_history):
                    if i > 0:
                        print("")
                    print(f"{LIGHT_PINK}    > {LIGHT_BLUE}{req}{RESET_COLOR}")
                if files_written:
                    print(f"\n{LIGHT_ORANGE} 📁 FILES UPDATED: {RESET_COLOR}")
                else:
                    print(f"\n{LIGHT_ORANGE} 📁 FILES TO UPDATE: {RESET_COLOR}")

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
            if files_written:
                print(
                    f"\n{LIGHT_ORANGE} ✅ {LIGHT_GREEN}CHANGESET WRITTEN {RESET_COLOR}\n"
                )
                files_written = False
            print(f"{LIGHT_ORANGE} ⚡️ ACTION: {RESET_COLOR}")
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
                written_files = write_files(files, args.dir)
                files_written = True
                for file_path in written_files:
                    if file_path.endswith((".sh")):
                        print(
                            f"\n ⚡️ {LIGHT_ORANGE}EXECUTABLE DETECTED{RESET_COLOR}"
                        )
                        print(
                            f"    - {LIGHT_PINK}{os.path.basename(file_path)}{RESET_COLOR}"
                        )
                        run_question = [
                            {
                                "type": "confirm",
                                "name": "run_script",
                                "message": f"Would you like to run {os.path.basename(file_path)}?",
                                "default": True,
                            }
                        ]
                        run_answer = prompt(run_question)
                        if run_answer["run_script"]:
                            print(
                                f"\n{LIGHT_ORANGE} 🏃‍♀️ Running {os.path.basename(file_path)}...{RESET_COLOR}"
                            )
                            run_script(file_path)
                            print(
                                f"\n{LIGHT_ORANGE} ✅ Script execution completed{RESET_COLOR}"
                            )

                            # Automatically reload files after running the script
                            reloaded_files = reload_files(args)
                            formatted_files = format_file_contents(
                                reloaded_files
                            )
                            messages.append(
                                {
                                    "role": "user",
                                    "content": f"My files have been updated after running the script, here is their latest state:\n\n{formatted_files}",
                                }
                            )
                            print(
                                f"\n{LIGHT_ORANGE} ✅ Files reloaded and appended to messages{RESET_COLOR}"
                            )
                            total_cost = display_token_count_and_cost(messages)
                            print(
                                f"{LIGHT_ORANGE} ℹ️  Updated token count and cost estimate shown above{RESET_COLOR}"
                            )
            elif answers["next_step"] == "🔄 Reload files":
                reloaded_files = reload_files(args)
                formatted_files = format_file_contents(reloaded_files)
                messages.append(
                    {
                        "role": "user",
                        "content": f"My files have been updated, here is their latest state:\n\n{formatted_files}",
                    }
                )
                print(
                    f"\n{LIGHT_ORANGE} ✅ Files reloaded and appended to messages{RESET_COLOR}"
                )
                total_cost = display_token_count_and_cost(messages)
                print(
                    f"{LIGHT_ORANGE} ℹ️  Updated token count and cost estimate shown above{RESET_COLOR}"
                )
            elif answers["next_step"] == "💬 Followup prompt":
                followup = input(f"     {LIGHT_PINK}> {LIGHT_BLUE}")
                messages.append({"role": "user", "content": followup})
                return answers
            elif answers["next_step"] == "🚪 Exit":
                return answers

    else:
        if args.auto_write:
            written_files = write_files(files, args.dir)
            print(f"\n{LIGHT_ORANGE} ✅ CHANGESET WRITTEN {RESET_COLOR}")
            for file_path in written_files:
                if file_path.endswith((".sh", ".py")):
                    print(
                        f"\n{LIGHT_ORANGE} 🚀 Running {os.path.basename(file_path)}...{RESET_COLOR}"
                    )
                    run_script(file_path)
                    print(
                        f"\n{LIGHT_ORANGE} ✅ Script execution completed{RESET_COLOR}"
                    )

                    # Automatically reload files after running the script
                    reloaded_files = reload_files(args)
                    formatted_files = format_file_contents(reloaded_files)
                    messages.append(
                        {
                            "role": "user",
                            "content": f"My files have been updated after running the script, here is their latest state:\n\n{formatted_files}",
                        }
                    )
                    print(
                        f"\n{LIGHT_ORANGE} ✅ Files reloaded and appended to messages{RESET_COLOR}"
                    )
                    total_cost = display_token_count_and_cost(messages)
                    print(
                        f"{LIGHT_ORANGE} ℹ️  Updated token count and cost estimate shown above{RESET_COLOR}"
                    )

    return answers

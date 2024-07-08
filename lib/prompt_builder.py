import io
import os
import requests
from contextlib import redirect_stdout
from bs4 import BeautifulSoup
from lib.file_io import get_files, print_files_as_tree, format_file_contents
from lib.prompt_templates import (
    QUESTION_PROMPT_PRE,
    AUTODEV_PROMPT_PRE,
    QUESTION_PROMPT_POST_TEMPLATE,
    AUTODEV_PROMPT_POST_TEMPLATE,
)
from lib.shell_util import (
    LIGHT_GREEN,
    LIGHT_ORANGE,
    RESET_COLOR,
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_RED,
)
from lib.embedding_util import get_top_relevant_files
from lib.litellm_client import raw_token_count
from lib.uploaded_file_filter import UploadedFileFilter


def build_prompt(args, requirements, files):
    """
    Build the prompt content by capturing standard output.

    Args:
        args (Namespace): The command line arguments.
        requirements (str): The user requirements.
        files (list): List of files fetched in the scan.

    Returns:
        str: The captured prompt content.
    """

    # Get all files we could upload (used for directory tree) and the
    # actual files we're going to upload, as well as the startpath
    all_files, files_to_upload, startpath = build_fileset(args, requirements)

    # Notify the user of the files to be uploaded
    if args.focused:
        print_focused_file_output(files_to_upload)
    else:
        print_inclusive_file_output(args, files_to_upload)

    f = io.StringIO()
    with redirect_stdout(f):
        if args.resources:
            print("\nResources:")
            for url in args.resources:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    body_content = str(soup.body)
                    print(f"\nURL: {url}\n{body_content}")
                except requests.RequestException as e:
                    print(f"Failed to fetch {url}: {e}")

        if args.mode == "question":
            print(QUESTION_PROMPT_PRE)
        else:
            print(AUTODEV_PROMPT_PRE)

        print("Directory Tree:")
        # Map all_files to paths
        all_file_paths = [file["path"] for file in all_files]
        print_files_as_tree(startpath, all_file_paths)

        print("\nFile Contents:")
        print(format_file_contents(files_to_upload))

        if args.mode == "question":
            prompt_post = QUESTION_PROMPT_POST_TEMPLATE.format(
                requirements="\n".join(args.requirements_history)
            )
        else:
            prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(
                requirements="\n".join(args.requirements_history)
            )

        print(prompt_post)

    return f.getvalue()

def build_fileset(args, requirements):
    startpath = args.dir

    # Build uploaded file filter
    upload_filter = UploadedFileFilter(
        startpath,
        args.ignore,
        args.max_file_size
    )

    all_files = get_files(startpath, upload_filter)

    if args.focused:
        files_to_upload = get_top_relevant_files(
            startpath=startpath,
            upload_filter=upload_filter,
            query=requirements,
            num_files=args.focused,
            model_embedding=args.model_embedding,
        )
    else:
        files_to_upload = all_files

    return (all_files, files_to_upload, startpath)

def print_focused_file_output(files):
    """
    Print the focused file output.

    Args:
        files (list): The focused file list.
    """
    print(
        f"\n{LIGHT_ORANGE} 🔬  FOCUSING ON {len(files)} MOST RELEVANT FILE CHUNKS: {RESET_COLOR}"
    )
    for file in files:
        print_focused_file_output_line(file)

def print_focused_file_output_line(file):
    """
    Print the focused file output.

    Args:
        file (dict): The focused file dictionary.
    """
    path = file["path"]
    score = round(file["score"], 2)
    print(
        f"    {LIGHT_PINK}* {LIGHT_BLUE}{path} {LIGHT_GREEN}({score}){RESET_COLOR}"
    )

def print_inclusive_file_output(args, files):
    """
    Print the inclusive file output.

    Args:
        files (list): The inclusive file list.
    """
    total = len(files)
    print(
        f"\n{LIGHT_ORANGE} 🗂️  INCLUDING {total:,} UNIGNORED FILES: {RESET_COLOR}"
    )
    for file in files:
        print_inclusive_file_output_line(args, file)

def print_inclusive_file_output_line(args, file):
    """
    Print the inclusive file output.

    Args:
        file (dict): The inclusive file dictionary.
    """
    path = file["path"]
    if args.debug:
        tokens = raw_token_count(file["data"], args.model)
        print(
            f"    {LIGHT_PINK}* {LIGHT_BLUE}{path} {LIGHT_RED}({tokens:,}){RESET_COLOR}"
        )
    else:
        print(f"    {LIGHT_PINK}* {LIGHT_BLUE}{path}")

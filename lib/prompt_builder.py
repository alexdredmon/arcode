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
from lib.image_util import process_image


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
        content = []
        
        if args.resources:
            content.append({"type": "text", "text": "\nResources:"})
            for url in args.resources:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    body_content = str(soup.body)
                    content.append({"type": "text", "text": f"\nURL: {url}\n{body_content}"})
                except requests.RequestException as e:
                    content.append({"type": "text", "text": f"Failed to fetch {url}: {e}"})

        if args.images:
            content.append({"type": "text", "text": "\nImages:"})
            for image_path in args.images:
                try:
                    image_data = process_image(image_path)
                    content.append({"type": "text", "text": f"\nImage: {image_path}"})
                    content.append({"type": "image_url", "image_url": {"url": image_data}})
                except Exception as e:
                    content.append({"type": "text", "text": f"Failed to process image {image_path}: {e}"})

        if args.mode == "question":
            content.append({"type": "text", "text": QUESTION_PROMPT_PRE})
        else:
            content.append({"type": "text", "text": AUTODEV_PROMPT_PRE})

        content.append({"type": "text", "text": "Directory Tree:"})
        # Map all_files to paths
        all_file_paths = [file["path"] for file in all_files]
        tree_output = io.StringIO()
        with redirect_stdout(tree_output):
            print_files_as_tree(startpath, all_file_paths)
        content.append({"type": "text", "text": tree_output.getvalue()})

        content.append({"type": "text", "text": "\nFile Contents:"})
        content.append({"type": "text", "text": format_file_contents(files_to_upload)})

        if args.mode == "question":
            prompt_post = QUESTION_PROMPT_POST_TEMPLATE.format(
                requirements="\n".join(args.requirements_history)
            )
        else:
            prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(
                requirements="\n".join(args.requirements_history)
            )

        content.append({"type": "text", "text": prompt_post})

        # Print the content for stdout capture
        for item in content:
            if item["type"] == "text":
                print(item["text"])
            elif item["type"] == "image_url":
                print(f"[Image URL: {item['image_url']['url']}]")

    return content

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

def reload_files(args):
    """
    Reload files from the working directory.

    Args:
        args (Namespace): The command line arguments.

    Returns:
        list: List of dictionaries containing file paths and data.
    """
    _, files_to_upload, _ = build_fileset(args, args.requirements_history[-1])
    return files_to_upload
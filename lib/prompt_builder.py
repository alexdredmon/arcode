import io
import requests
from contextlib import redirect_stdout
from bs4 import BeautifulSoup
from lib.file_util import get_files, print_tree, format_file_contents
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


def build_prompt(args, requirements, startpath, ignore_patterns, files):
    """
    Build the prompt content by capturing standard output.

    Args:
        args (Namespace): The command line arguments.
        requirements (str): The user requirements.
        startpath (str): The starting directory path.
        ignore_patterns (list): List of patterns to ignore during directory scan.
        files (list): List of files fetched in the scan.

    Returns:
        str: The captured prompt content.
    """
    if args.focused:
        files = get_top_relevant_files(
            startpath=startpath,
            ignore_patterns=ignore_patterns,
            query=requirements,
            num_files=args.focused,
            model_embedding=args.model_embedding,
        )
        print(
            f"\n{LIGHT_ORANGE} 🔬  FOCUSING ON {args.focused} MOST RELEVANT FILE CHUNKS: {RESET_COLOR}"
        )
        for file in files:
            path = file["path"]
            score = round(file["score"], 2)
            print(
                f"    {LIGHT_PINK}* {LIGHT_BLUE}{path} {LIGHT_GREEN}({score}){RESET_COLOR}"
            )
    else:
        files = get_files(startpath, ignore_patterns)
        total = len(files)
        print(
            f"\n{LIGHT_ORANGE} 🗂️  INCLUDING {total:,} UNIGNORED FILES: {RESET_COLOR}"
        )
        for file in files:
            path = file["path"]
            if args.token_count_by_file:
                tokens = raw_token_count(file["data"], args.token_encoding)
                print(
                    f"    {LIGHT_PINK}* {LIGHT_BLUE}{path} {LIGHT_RED}({tokens:,}){RESET_COLOR}"
                )
            else:
                print(f"    {LIGHT_PINK}* {LIGHT_BLUE}{path}")

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
        print_tree(startpath, ignore_patterns)

        print("\nFile Contents:")
        print(format_file_contents(files))

        if args.mode == "question":
            prompt_post = QUESTION_PROMPT_POST_TEMPLATE.format(
                requirements=requirements
            )
        else:
            prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.format(
                requirements=requirements
            )

        print(prompt_post)

    return f.getvalue()

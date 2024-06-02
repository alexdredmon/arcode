import os
import argparse
import sys
import io
from contextlib import redirect_stdout
from openai import OpenAI
from config import API_KEY


AUTODEV_PROMPT_PRE = """
You are a software development team.  I'm going to provide you with your codebase, then we'll build some features.

Here's my codebase:
"""

AUTODEV_PROMPT_POST_TEMPLATE = """
That's my codebase.

I will ask you to build features on top of the codebase - respond first with the files that need to be changed followed by a brief summary of the changes. Only output files that require changes to implement the current feature. When you output the files, begin with the filename of the file being updated and then output the entire un-truncated file after modifications. Do not remove any comments. Ensure that the first line of each file is "// FILENAME" where "FILENAME" is the file's name, and that the last line of each file is "// eof" - and most importantly, make sure to surround each file with triple backticks "```" so that they will be entirely formatted as code.

Here are the features I need you to build:
[REQUIREMENTS]
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description="A CLI program to display a directory tree and file contents.")
    parser.add_argument('--dir', type=str, default='.', help='The working directory of the codebase, default to current directory.')
    parser.add_argument('requirements', nargs='*', type=str, help='Requirements for features to build on the codebase.')
    return parser.parse_args()

def print_tree(startpath, prefix=''):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{prefix}{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{prefix}{subindent}{f}')

def print_file_contents(startpath):
    for root, _, files in os.walk(startpath):
        for f in files:
            file_path = os.path.relpath(os.path.join(root, f), startpath)
            print(f"**************** FILE: {file_path} ****************")
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                    print(file.read())
            except UnicodeDecodeError as e:
                print(f"Error reading file {file_path}: {e}")
            print(f"**************** EOF ****************")

def main():
    args = parse_arguments()

    if sys.stdin.isatty():
        requirements = ' '.join(args.requirements)
    else:
        requirements = sys.stdin.read().strip()

    f = io.StringIO()
    with redirect_stdout(f):
        print(AUTODEV_PROMPT_PRE)

        startpath = args.dir

        print("Directory Tree:")
        print_tree(startpath)

        print("\nFile Contents:")
        print_file_contents(startpath)

        autodev_prompt_post = AUTODEV_PROMPT_POST_TEMPLATE.replace("[REQUIREMENTS]", requirements)
        print(autodev_prompt_post)

    USER_CONTENT = f.getvalue()

    # Ensure the API key is set
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_CONTENT}
        ],
        stream=True
    )

    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content"):
            print(delta.content, end="", flush=True)
        else:
            print(f"Chunk received: {chunk}", flush=True)

if __name__ == "__main__":
    main()

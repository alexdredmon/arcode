import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="A CLI program to display a directory tree and file contents.")
    parser.add_argument('--dir', type=str, default='.', help='The working directory of the codebase, default to current directory.')
    parser.add_argument('requirements', nargs='*', type=str, help='Requirements for features to build on the codebase.')
    return parser.parse_args()

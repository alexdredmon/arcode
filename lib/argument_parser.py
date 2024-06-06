import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="arcode: AI driven development tool")
    parser.add_argument('--dir', type=str, default='.', help='The working directory of the codebase, default to current directory.')
    parser.add_argument('--write', type=bool, default=False, help='Whether or not to write the changeset immediately.  If piping input to arcode, this defaults to true.')
    parser.add_argument('--focused', type=int, default=0, help='Enable focused mode to limit files based on relevancy using embeddings - accepts an integer containing number of files to limit context to.')
    parser.add_argument('--model', type=str, default='openai/gpt-4o', help='Specify the LLM provider/model to use with LiteLLM, default to openai/gpt-4o.')
    parser.add_argument('requirements', nargs='*', type=str, help='Requirements for features to build on the codebase.')
    
    return parser.parse_args()

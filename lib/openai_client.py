from openai import OpenAI

AUTODEV_PROMPT_PRE = """
You are a software development team. I'm going to provide you with your codebase, then we'll build some features.

Take careful care to follow the requested response format, using "===.= ==== FILENAME: file1.py = ===== =========" and "===.= ==== EOF = ===== =========" delimiters when outputting files and "SUMMARY:" and "FILES:" section headers to indicate the respective parts of the chat completion response.
Always include an "ESTIMATED CHARACTERS:" heading followed by an estimated number of total characters in the modified files after implementing the requested changes (i.e. total number of characters in these files, not just the number of characters changed)- it is fine if this number is not exact but always provide an estimate and express it with digits only (no commas/formatting).

Here's my codebase:
"""

AUTODEV_PROMPT_POST_TEMPLATE = """
That's my codebase.

Here are the features I need you to build:
{requirements}

Return a brief summary of changes, estimated character count of all modified files, and the complete contents of each file required to be modified/created in the implementation of these requirements - no truncation.
Your response should follow the following format:

## SUMMARY:
[Changing X to implement Y, lorem ipsum]
- Change 1 in file1.py
- Change 2 in file1.py
- Change 3 in lib/file2.py

## ESTIMATED CHARACTERS:
1234

## FILES:
===.= ==== FILENAME: demofile1.py = ===== =========
```python
import requests

print("Hello world")
```
===.= ==== EOF: demofile1.py = ===== =========
===.= ==== FILENAME: lib/demofile2.py = ===== =========
# Just another demo file
===.= ==== EOF: lib/demofile2.py = ===== =========
"""

LIGHT_PINK = '\033[95m'
LIGHT_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

def create_openai_client(api_key):
    return OpenAI(api_key=api_key)

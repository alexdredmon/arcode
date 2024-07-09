from litellm.llms.openai import OpenAIError
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound
from lib.file_parser import (
    parse_files,
)
from lib.file_parser import (
    extract_filename_start,
    extract_filename_end,
)
from lib.shell_util import (
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_ORANGE,
    BLACK_BACKGROUND,
    LIGHT_RED,
    RESET_COLOR,
)

def stream_response(client, args, messages):
    """
    Stream the response from the LLM client and handle file updates and formatting.

    Args:
        client (object): The LLM client instance to use for streaming responses.
        args (Namespace): Parsed command line arguments.
        messages (list): Messages to send to the LLM client.

    Returns:
        tuple: A tuple containing a list of updated files and the streamed response text.
    """
    files = []
    streamed_response = ""

    try:
        completion = client(model=args.model, messages=messages, stream=True)

        print(f"\n{LIGHT_ORANGE} 🌐 STREAMING RESPONSE: {RESET_COLOR}\n")
        streamed_response = ""
        response_chunks = []
        output_padding = "    "
        print(f"{LIGHT_BLUE}", end="", flush=True)
        since_last_line = ""
        latest_line = None
        last_was_file_header = False
        language = "python"
        lexer = None

        formatter = TerminalFormatter()
        for chunk in completion:
            if (
                chunk
                and chunk.choices
                and chunk.choices[0]
                and chunk.choices[0].delta
            ):
                delta = chunk.choices[0].delta
                if delta.get("content"):
                    content = delta["content"]
                    response_chunks.append(content)
                    streamed_response += content
                    since_last_line += content
                    while "\n" in since_last_line:
                        bits = since_last_line.splitlines()
                        latest_line = bits[0]

                        filename = extract_filename_start(latest_line)
                        is_file_header = filename != None
                        if is_file_header:
                            latest_line = (
                                f"\n{output_padding}═ 📄 {filename} "
                                + "═" * (60 - len(filename))
                            )

                        filename = extract_filename_end(latest_line)
                        is_file_footer = filename != None
                        if is_file_footer:
                            latest_line = (
                                f"═ EOF: {filename} "
                                + "═" * (58 - len(filename))
                                + "\n"
                            )

                        if is_file_header or is_file_footer:
                            print(LIGHT_PINK, end="", flush=True)

                        if last_was_file_header and "```" in latest_line:
                            language = latest_line.replace("```", "")
                            if language == "plaintext":
                                language = "plain"
                            if language == "tsx":
                                language = "typescript"
                            if language:
                                try:
                                    lexer = get_lexer_by_name(language)
                                except ClassNotFound:
                                    lexer = None
                                latest_line = (
                                    " " * (66 - len(language)) + language
                                )
                        if is_file_footer:
                            language = None
                            lexer = None

                        if lexer:
                            latest_line = highlight(
                                latest_line, lexer, formatter
                            )
                            if latest_line.endswith("\n"):
                                latest_line = latest_line[:-1]

                        print(f"{output_padding}{latest_line}")

                        if is_file_header:
                            print(LIGHT_ORANGE, end="", flush=True)
                            last_was_file_header = True
                        else:
                            last_was_file_header = False
                        if is_file_footer:
                            print(LIGHT_BLUE, end="", flush=True)

                        since_last_line = "\n".join(bits[1:])
        filename = extract_filename_end(since_last_line)
        if filename:
            since_last_line = f"═ EOF: {filename} " + "═" * (
                58 - len(filename)
            )
            print(f"{output_padding}{LIGHT_PINK}{since_last_line}")
        else:
            print(f"{output_padding}{LIGHT_BLUE}{since_last_line}")

    except OpenAIError as e:
        print(f"{BLACK_BACKGROUND}{LIGHT_RED}{e.message}{RESET_COLOR}")

    files = parse_files(streamed_response)
    messages.append({"role": "assistant", "content": streamed_response})

    return files, streamed_response
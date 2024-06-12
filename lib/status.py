from lib.shell_util import (
    LIGHT_PINK,
    LIGHT_BLUE,
    WHITE_ON_BLACK,
    BLACK_ON_WHITE,
    RESET_COLOR,
)

def print_configuration(args, requirements):
    print(
        f"""
{WHITE_ON_BLACK} 🏗️  {BLACK_ON_WHITE} BUILDING FEATURE(S): {RESET_COLOR}
{LIGHT_PINK}> {LIGHT_BLUE}{requirements}{RESET_COLOR}
{WHITE_ON_BLACK} ⚙️  {BLACK_ON_WHITE} CONFIGURATION: {RESET_COLOR}
{LIGHT_PINK}        Config file: {LIGHT_BLUE}{args.config_from_file}{RESET_COLOR}
{LIGHT_PINK}          Directory: {LIGHT_BLUE}{args.dir}{RESET_COLOR}
{LIGHT_PINK}              Model: {LIGHT_BLUE}{args.model}{RESET_COLOR}
{LIGHT_PINK}    Embedding Model: {LIGHT_BLUE}{args.model_embedding}{RESET_COLOR}
{LIGHT_PINK}     Token Encoding: {LIGHT_BLUE}{args.token_encoding}{RESET_COLOR}
{LIGHT_PINK}         Auto-write: {LIGHT_BLUE}{args.autowrite}{RESET_COLOR}
{LIGHT_PINK}            Focused: {LIGHT_BLUE}{args.focused}{RESET_COLOR}
{LIGHT_PINK}             Ignore: {LIGHT_BLUE}{args.ignore}{RESET_COLOR}
{LIGHT_PINK}               Mode: {LIGHT_BLUE}{args.mode}{RESET_COLOR}
{LIGHT_PINK}          Resources: {LIGHT_BLUE}{args.resources}{RESET_COLOR}
    """
    )

def print_tokens(input_tokens, output_tokens, total_tokens, token_encoding):
    print(
        f"""
{WHITE_ON_BLACK} 🧮 {BLACK_ON_WHITE} TOKENS ({total_tokens:,} total) [{token_encoding}]{RESET_COLOR}
    {LIGHT_PINK}In: {LIGHT_BLUE}{input_tokens:,}{RESET_COLOR}
    {LIGHT_PINK}Out: {LIGHT_BLUE}{output_tokens:,}{RESET_COLOR}
                """
    )
from lib.shell_util import (
    LIGHT_GREEN,
    LIGHT_ORANGE,
    LIGHT_PINK,
    LIGHT_BLUE,
    RESET_COLOR,
)
from lib.cost_estimator import CostEstimator


def print_configuration(args, requirements):
    print(
        f"""
{LIGHT_ORANGE} 🏗️  BUILDING FEATURE: {RESET_COLOR}
{LIGHT_PINK}    > {LIGHT_BLUE}{requirements}{RESET_COLOR}

{LIGHT_ORANGE} ⚙️  CONFIGURATION: {RESET_COLOR}
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


def print_tokens(
    input_tokens, output_tokens, total_tokens, token_encoding, model
):
    cost_estimator = CostEstimator()
    input_cost, output_cost, total_cost = cost_estimator.calculate_cost(
        model, input_tokens, output_tokens
    )

    print(
        f"""
{LIGHT_ORANGE} 🧮 TOKENS [{token_encoding}]{RESET_COLOR}
    {LIGHT_PINK}   In: {LIGHT_BLUE}{input_tokens:,}{RESET_COLOR}
    {LIGHT_PINK}  Out: {LIGHT_BLUE}{output_tokens:,}{RESET_COLOR}
    {LIGHT_PINK}Total: {LIGHT_BLUE}{total_tokens:,}{RESET_COLOR}"""
    )
    if total_cost:
        print(
            f"""
{LIGHT_ORANGE} 💰 COST ESTIMATE{RESET_COLOR}
{LIGHT_PINK}    Cost: {LIGHT_GREEN}${total_cost:,.2f}{RESET_COLOR}
"""
        )

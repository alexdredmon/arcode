from lib.shell_util import (
    LIGHT_GREEN,
    LIGHT_ORANGE,
    LIGHT_PINK,
    LIGHT_BLUE,
    LIGHT_RED,
    RESET_COLOR,
)
from litellm import cost_per_token


def print_configuration(args, requirements):
    try:
        max_cost = "${:.2f}".format(float(args.max_estimated_cost))
    except (ValueError, TypeError):
        max_cost = "N/A"

    print(
        LIGHT_ORANGE + " 🏗️  BUILDING FEATURE: " + RESET_COLOR + "\n" +
        LIGHT_PINK + "    > " + LIGHT_BLUE + str(requirements) + RESET_COLOR + "\n\n" +
        LIGHT_ORANGE + " ⚙️  CONFIGURATION: " + RESET_COLOR + "\n" +
        LIGHT_PINK + "          Directory: " + LIGHT_BLUE + str(args.dir) + RESET_COLOR + "\n" +
        LIGHT_PINK + "              Model: " + LIGHT_BLUE + str(args.model) + RESET_COLOR + "\n" +
        LIGHT_PINK + "         Max tokens: " + LIGHT_BLUE + str(args.max_tokens) + RESET_COLOR + "\n" +
        LIGHT_PINK + "        Temperature: " + LIGHT_BLUE + str(args.temperature) + RESET_COLOR + "\n" +
        LIGHT_PINK + "    Embedding Model: " + LIGHT_BLUE + str(args.model_embedding) + RESET_COLOR + "\n" +
        LIGHT_PINK + "         Auto-write: " + LIGHT_BLUE + str(args.auto_write) + RESET_COLOR + "\n" +
        LIGHT_PINK + "            Focused: " + LIGHT_BLUE + str(args.focused) + RESET_COLOR + "\n" +
        LIGHT_PINK + "             Ignore: " + LIGHT_BLUE + str(args.ignore) + RESET_COLOR + "\n" +
        LIGHT_PINK + "               Mode: " + LIGHT_BLUE + str(args.mode) + RESET_COLOR + "\n" +
        LIGHT_PINK + "          Resources: " + LIGHT_BLUE + str(args.resources) + RESET_COLOR + "\n" +
        LIGHT_PINK + "           Image(s): " + LIGHT_BLUE + str(args.images) + RESET_COLOR + "\n" +
        LIGHT_PINK + "      Max Est. Cost: " + LIGHT_BLUE + max_cost + RESET_COLOR + "\n" +
        LIGHT_PINK + "      Max File Size: " + LIGHT_BLUE + "{:,} bytes".format(args.max_file_size) + RESET_COLOR + "\n"
    )


def print_tokens(token_counts):
    """
    Print token counts and estimated cost.

    Args:
        token_counts (dict): A dictionary containing token counts and model information.

    Returns:
        float: The total estimated cost.
    """
    model = token_counts['model']
    input_cost, output_cost = cost_per_token(
        model=model,
        prompt_tokens=token_counts["input_tokens"],
        completion_tokens=token_counts["output_tokens"],
    )
    total_cost = input_cost + output_cost

    print(
        f"""
{LIGHT_ORANGE} 🧮 TOKENS{RESET_COLOR}
    {LIGHT_PINK}Content: {LIGHT_BLUE}{token_counts['content_tokens']:,}{RESET_COLOR}
    {LIGHT_PINK} Images: {LIGHT_BLUE}{token_counts['image_tokens']:,}{RESET_COLOR}
    {LIGHT_PINK}     In: {LIGHT_BLUE}{token_counts['input_tokens']:,}{RESET_COLOR}
    {LIGHT_PINK}    Out: {LIGHT_BLUE}{token_counts['output_tokens']:,}{RESET_COLOR}
    {LIGHT_PINK}  Total: {LIGHT_BLUE}{token_counts['total_tokens']:,}{RESET_COLOR}"""
    )
    if total_cost:
        print(
            f"""
{LIGHT_ORANGE} 💰 COST ESTIMATE{RESET_COLOR}
{LIGHT_PINK}    Cost: {LIGHT_GREEN}${total_cost:,.2f}{RESET_COLOR}
"""
        )
    return total_cost


def check_cost_exceeds_maximum(total_cost, maximum_cost):
    """
    Check if the estimated cost exceeds the maximum allowed cost.

    Args:
        total_cost (float): The estimated total cost.
        maximum_cost (float): The maximum allowed cost.

    Returns:
        bool: True if the cost exceeds the maximum, False otherwise.
    """
    if total_cost > maximum_cost:
        print(
            f"\n{LIGHT_RED}⚠️  WARNING: Estimated cost (${total_cost:.2f}) exceeds the maximum allowed cost (${maximum_cost:.2f}).{RESET_COLOR}"
        )
        return True
    return False
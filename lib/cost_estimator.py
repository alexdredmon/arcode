class CostEstimator:
    """
    A class to calculate cost estimates for requests based on the token counts.
    """

    def __init__(self):
        self.model_costs = {
            "openai/gpt-4o": {
                "input_cost_per_million": 5,
                "output_cost_per_million": 15,
            },
            "anthropic/claude-3-opus-20240229": {
                "input_cost_per_million": 15,
                "output_cost_per_million": 75,
            },
            "azure/gpt-4o": {
                "input_cost_per_million": 5,
                "output_cost_per_million": 15,
            },
        }

    def calculate_cost(self, model, input_tokens, output_tokens):
        """
        Calculate the cost based on the number of input and output tokens.

        Args:
            model (str): The model identifier.
            input_tokens (int): The number of input tokens.
            output_tokens (int): The number of output tokens.

        Returns:
            tuple: The cost for input tokens, output tokens, and total cost.
        """
        if model not in self.model_costs:
            return None, None, None

        input_cost_per_million = self.model_costs[model][
            "input_cost_per_million"
        ]
        output_cost_per_million = self.model_costs[model][
            "output_cost_per_million"
        ]

        input_cost = (input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (output_tokens / 1_000_000) * output_cost_per_million
        total_cost = input_cost + output_cost

        return input_cost, output_cost, total_cost

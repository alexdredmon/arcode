import tiktoken
from lib.image_util import calculate_image_token_cost
from lib.status import print_tokens as _print_tokens
from lib.shell_util import (
    LIGHT_BLUE,
    RESET_COLOR,
)

class TokenCounter:
    def __init__(self, model):
        self.model = model
        self.encoding = self._get_encoding(model)
        self.reset_counts()

    def _get_encoding(self, model):
        try:
            return tiktoken.encoding_for_model(model.split("/")[-1])
        except Exception:
            print(
                f"{LIGHT_BLUE} 💁‍♀️ Defaulting to 'cl100k_base' - no model-specific encoding for {model}.{RESET_COLOR}"
            )
            return tiktoken.get_encoding("cl100k_base")

    def reset_counts(self):
        self.token_counts = {
            "content_tokens": 0,
            "image_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "model": self.model
        }

    def count_tokens(self, messages):
        self.reset_counts()

        for message in messages:
            if isinstance(message["content"], list):
                for content_item in message["content"]:
                    if content_item["type"] == "text":
                        tokens = len(self.encoding.encode(content_item["text"], disallowed_special=()))
                        self.token_counts["content_tokens"] += tokens
                        if message["role"] == "user":
                            self.token_counts["input_tokens"] += tokens
                        else:
                            self.token_counts["output_tokens"] += tokens
                    elif content_item["type"] == "image_url":
                        tokens = len(self.encoding.encode(content_item["image_url"]["url"], disallowed_special=()))
                        self.token_counts["image_tokens"] += tokens
                        self.token_counts["input_tokens"] += tokens
                        # Image tokens are counted separately and not added to input/output here
                        pass
            else:
                tokens = len(self.encoding.encode(message["content"], disallowed_special=()))
                self.token_counts["content_tokens"] += tokens
                if message["role"] == "user":
                    self.token_counts["input_tokens"] += tokens
                else:
                    self.token_counts["output_tokens"] += tokens

        self.update_total_tokens()
        return self.token_counts

    def add_initial_image_tokens(self, image_paths):
        total_image_tokens = 0
        for image_path in image_paths:
            image_tokens = calculate_image_token_cost(image_path, self.encoding)
            total_image_tokens += image_tokens
        self.token_counts["image_tokens"] += total_image_tokens
        self.token_counts["input_tokens"] += total_image_tokens
        self.token_counts["content_tokens"] += total_image_tokens
        self.update_total_tokens()
        return self.token_counts

    def add_image_tokens(self, image_paths):
        total_image_tokens = 0
        for image_path in image_paths:
            image_tokens = calculate_image_token_cost(image_path, self.encoding)
            total_image_tokens += image_tokens
        self.token_counts["image_tokens"] += total_image_tokens
        self.update_total_tokens()
        return self.token_counts

    def update_total_tokens(self):
        self.token_counts["total_tokens"] = self.token_counts["input_tokens"] + self.token_counts["output_tokens"]

    def print_tokens(self):
        return _print_tokens(self.token_counts)

token_counter = None

def initialize_token_counter(model):
    global token_counter
    token_counter = TokenCounter(model)

def get_token_counts(messages):
    global token_counter
    if token_counter is None:
        raise ValueError("Token counter not initialized. Call initialize_token_counter first.")
    return token_counter.count_tokens(messages)

def add_initial_image_tokens(image_paths):
    global token_counter
    if token_counter is None:
        raise ValueError("Token counter not initialized. Call initialize_token_counter first.")
    return token_counter.add_initial_image_tokens(image_paths)

def add_image_tokens(image_paths):
    global token_counter
    if token_counter is None:
        raise ValueError("Token counter not initialized. Call initialize_token_counter first.")
    return token_counter.add_image_tokens(image_paths)

def print_token_counts():
    global token_counter
    if token_counter is None:
        raise ValueError("Token counter not initialized. Call initialize_token_counter first.")
    return token_counter.print_tokens()
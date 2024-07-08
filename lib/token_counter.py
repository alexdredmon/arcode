import tiktoken
from lib.image_util import calculate_image_token_cost
from lib.status import print_tokens as _print_tokens

class TokenCounter:
    def __init__(self, model):
        self.model = model
        self.encoding = self._get_encoding(model)
        self.token_counts = {
            "content_tokens": 0,
            "image_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "model": model
        }

    def _get_encoding(self, model):
        try:
            return tiktoken.encoding_for_model(model.split("/")[-1])
        except Exception:
            print(f" ⚠️  No model-specific encoding for {model}, defaulting to 'cl100k_base'.")
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, messages):
        self.token_counts = {
            "content_tokens": 0,
            "image_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "model": self.model
        }

        for message in messages:
            if message["role"] == "user":
                if isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if content_item["type"] == "text":
                            tokens = len(self.encoding.encode(content_item["text"], disallowed_special=()))
                            self.token_counts["content_tokens"] += tokens
                            self.token_counts["input_tokens"] += tokens
                        elif content_item["type"] == "image_url":
                            image_url = content_item["image_url"]["url"]
                            tokens = len(self.encoding.encode(image_url, disallowed_special=()))
                            self.token_counts["image_tokens"] += tokens
                            self.token_counts["input_tokens"] += tokens
                else:
                    tokens = len(self.encoding.encode(message["content"], disallowed_special=()))
                    self.token_counts["content_tokens"] += tokens
                    self.token_counts["input_tokens"] += tokens
            else:
                if isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if content_item["type"] == "text":
                            tokens = len(self.encoding.encode(content_item["text"], disallowed_special=()))
                            self.token_counts["content_tokens"] += tokens
                            self.token_counts["output_tokens"] += tokens
                        elif content_item["type"] == "image_url":
                            image_url = content_item["image_url"]["url"]
                            tokens = len(self.encoding.encode(image_url, disallowed_special=()))
                            self.token_counts["image_tokens"] += tokens
                            self.token_counts["output_tokens"] += tokens
                else:
                    tokens = len(self.encoding.encode(message["content"], disallowed_special=()))
                    self.token_counts["content_tokens"] += tokens
                    self.token_counts["output_tokens"] += tokens

        self.token_counts["total_tokens"] = self.token_counts["input_tokens"] + self.token_counts["output_tokens"]
        return self.token_counts

    def add_image_tokens(self, image_paths):
        for image_path in image_paths:
            image_tokens = calculate_image_token_cost(image_path, self.encoding)
            self.token_counts["image_tokens"] += image_tokens
            self.token_counts["input_tokens"] += image_tokens
            self.token_counts["total_tokens"] += image_tokens
        return self.token_counts

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
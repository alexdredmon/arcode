import unittest
from unittest.mock import patch, MagicMock
from lib.litellm_client import create_litellm_client, calculate_token_count

class TestLitellmClient(unittest.TestCase):

    @patch('lib.litellm_client.get_api_keys')
    def test_create_litellm_client(self, mock_get_api_keys):
        mock_get_api_keys.return_value = "api_key"
        client = create_litellm_client("model")
        self.assertIsNotNone(client)

    @patch('tiktoken.get_encoding')
    def test_calculate_token_count(self, mock_get_encoding):
        mock_encode = MagicMock()
        mock_encode.encode.return_value = [1, 2, 3]
        mock_get_encoding.return_value = mock_encode
        input_tokens, output_tokens, total_tokens = calculate_token_count("model", [{"role": "user", "content": "hello"}])
        self.assertEqual(input_tokens, 3)
        self.assertEqual(output_tokens, 0)
        self.assertEqual(total_tokens, 3)

if __name__ == '__main__':
    unittest.main()
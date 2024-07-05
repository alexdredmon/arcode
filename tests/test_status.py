import unittest
from unittest.mock import patch, MagicMock
from lib.status import print_configuration, print_tokens

class TestStatus(unittest.TestCase):

    @patch('builtins.print')
    def test_print_configuration(self, mock_print):
        # Create a mock args object
        mock_args = MagicMock()
        mock_args.dir = "test_dir"
        mock_args.model = "test_model"
        mock_args.model_embedding = "test_embedding_model"
        mock_args.autowrite = False
        mock_args.focused = 0
        mock_args.ignore = ["ignore1", "ignore2"]
        mock_args.mode = "implement"
        mock_args.resources = ["resource1", "resource2"]

        # Call the function
        print_configuration(mock_args, "Test requirements")

        # Assert that print was called (we're not checking the exact output here)
        mock_print.assert_called()

    @patch('builtins.print')
    @patch('lib.status.cost_per_token')
    def test_print_tokens(self, mock_cost_per_token, mock_print):
        # Mock the cost_per_token function
        mock_cost_per_token.return_value = (0.01, 0.02)

        # Call the function
        print_tokens(100, 200, 300, "test_model")

        # Assert that print and cost_per_token were called
        mock_print.assert_called()
        mock_cost_per_token.assert_called_once_with(
            model="test_model",
            prompt_tokens=100,
            completion_tokens=200
        )

if __name__ == '__main__':
    unittest.main()
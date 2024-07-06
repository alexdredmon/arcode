from io import StringIO
import unittest
from unittest.mock import patch, MagicMock
from lib.user_menu import handle_user_menu

class TestUserMenu(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    @patch('lib.user_menu.prompt')
    @patch('lib.user_menu.calculate_token_count')
    @patch('lib.user_menu.print_tokens')
    @patch('lib.user_menu.write_files')
    def test_handle_user_menu(self, mock_write_files, mock_print_tokens, mock_calculate_token_count, mock_prompt, mock_stdout):
        # Mock the necessary functions and their return values
        mock_prompt.return_value = {"next_step": "🚪 Exit"}
        mock_calculate_token_count.return_value = (100, 50, 150)

        mock_print_tokens.return_value = 0.10

        # Create mock objects
        mock_args = MagicMock()
        mock_args.dir = "test_dir"
        mock_args.model = "test_model"
        mock_args.mode = "implement"
        mock_args.requirements_history = ["Test requirement"]
        mock_args.autowrite = False
        mock_args.maximumEstimatedCost = 5.0

        mock_files = [{"filename": "test.py", "contents": "print('test')"}]
        mock_messages = [{"role": "user", "content": "Test message"}]
        mock_streamed_response = "Test response"

        # Call the function
        result = handle_user_menu(mock_args, mock_files, mock_messages, mock_streamed_response)

        # Assert the results
        self.assertEqual(result, {"next_step": "🚪 Exit"})

        # Verify that the mocked functions were called
        mock_calculate_token_count.assert_called_once_with("test_model", mock_messages)
        mock_print_tokens.assert_called_once_with(100, 50, 150, "test_model")
        mock_prompt.assert_called_once()
        mock_write_files.assert_not_called()  # Since autowrite is False

    @patch('sys.stdout', new_callable=StringIO)
    @patch('lib.user_menu.prompt')
    @patch('lib.user_menu.calculate_token_count')
    @patch('lib.user_menu.print_tokens')
    @patch('lib.user_menu.write_files')
    def test_handle_user_menu_autowrite(self, mock_write_files, mock_print_tokens, mock_calculate_token_count, mock_prompt, mock_stdout):
        # Mock the necessary functions and their return values
        mock_prompt.return_value = {"next_step": "🚪 Exit"}
        mock_calculate_token_count.return_value = (100, 50, 150)

        # Test the autowrite functionality
        mock_args = MagicMock()
        mock_args.dir = "test_dir"
        mock_args.model = "test_model"
        mock_args.mode = "implement"
        mock_args.requirements_history = ["Test requirement"]
        mock_args.autowrite = True
        mock_args.maximumEstimatedCost = 5.0

        mock_files = [{"filename": "test.py", "contents": "print('test')"}]
        mock_messages = [{"role": "user", "content": "Test message"}]
        mock_streamed_response = "Test response"

        handle_user_menu(mock_args, mock_files, mock_messages, mock_streamed_response)

        # Verify that write_files was called when autowrite is True
        mock_write_files.assert_called_once_with(mock_files, "test_dir")

if __name__ == '__main__':
    unittest.main()
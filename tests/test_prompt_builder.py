from io import StringIO
import unittest
from unittest.mock import MagicMock, patch
from lib.prompt_builder import build_prompt

class TestPromptBuilder(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    @patch("lib.prompt_builder.get_top_relevant_files")
    @patch("lib.prompt_builder.get_files")
    @patch("lib.prompt_builder.print_files_as_tree")
    @patch("lib.prompt_builder.format_file_contents")
    @patch("lib.prompt_builder.process_image")
    @patch("requests.get")
    def test_build_prompt(
        self,
        mock_requests_get,
        mock_process_image,
        mock_format_file_contents,
        mock_print_files_as_tree,
        mock_get_files,
        mock_get_top_relevant_files,
        mock_stdout,
    ):
        # Mock setup
        mock_get_top_relevant_files.return_value = [
            {"path": "file1.py", "data": "Some content", "score": 0.9}
        ]
        mock_get_files.return_value = [
            {"path": "file1.py", "data": "Some content"}
        ]
        mock_print_files_as_tree.return_value = "file1.py"
        mock_format_file_contents.return_value = "Formatted Contents"
        mock_process_image.return_value = "base64_encoded_image_data"
        
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.content = "<html><body>Mocked HTML content</body></html>"
        mock_requests_get.return_value = mock_response

        # Setup args
        args = MagicMock()
        args.focused = False
        args.resources = ["http://example.com"]
        args.images = ["image1.jpg"]
        args.mode = "implement"
        args.model_embedding = "openai/text-embedding-3-small"
        args.dir = "startpath"
        args.ignore = []
        args.debug = False
        args.max_file_size = 1000000

        # Call the function
        prompt_content = build_prompt(args, "requirements", [])

        # Assertions
        self.assertIsInstance(prompt_content, list)
        self.assertTrue(any("Resources:" in item["text"] for item in prompt_content if item["type"] == "text"))
        self.assertTrue(any("Images:" in item["text"] for item in prompt_content if item["type"] == "text"))
        self.assertTrue(any("Directory Tree:" in item["text"] for item in prompt_content if item["type"] == "text"))
        self.assertTrue(any("File Contents:" in item["text"] for item in prompt_content if item["type"] == "text"))
        
        # Check for image content
        self.assertTrue(any(item["type"] == "image_url" for item in prompt_content))

        # Verify that the mocked functions were called
        mock_get_files.assert_called_once()
        mock_print_files_as_tree.assert_called_once()
        mock_format_file_contents.assert_called_once()
        mock_process_image.assert_called_once_with("image1.jpg")
        mock_requests_get.assert_called_once_with("http://example.com")

if __name__ == "__main__":
    unittest.main()
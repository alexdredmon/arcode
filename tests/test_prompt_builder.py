from io import StringIO
import unittest
from unittest.mock import MagicMock, patch
from lib.prompt_builder import build_prompt


class TestPromptBuilder(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    @patch("lib.prompt_builder.get_top_relevant_files")
    @patch("lib.prompt_builder.get_files")
    @patch("lib.prompt_builder.print_tree")
    @patch("lib.prompt_builder.format_file_contents")
    def test_build_prompt(
        self,
        mock_format_file_contents,
        mock_print_tree,
        mock_get_files,
        mock_get_top_relevant_files,
        mock_stdout,
    ):
        mock_get_top_relevant_files.return_value = [
            {"path": "file1.py", "data": "Some content"}
        ]
        mock_get_files.return_value = [
            {"path": "file1.py", "data": "Some content"}
        ]
        mock_print_tree.return_value = "file1.py"
        mock_format_file_contents.return_value = "Formatted Contents"
        args = MagicMock()
        args.focused = False
        args.resources = ["http://example.com"]
        args.mode = "implement"
        args.model_embedding = "openai/text-embedding-3-small"
        prompt = build_prompt(
            args, "requirements", "startpath", ["ignore_pattern"], []
        )
        self.assertIn("Directory Tree:", prompt)
        self.assertIn("Formatted Contents", prompt)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch


class TestEmbeddingUtil(unittest.TestCase):
    @patch("lib.embedding_util.get_top_relevant_files")
    def test_get_top_relevant_files(self, mock_get_top_relevant_files):
        # Mock the get_top_relevant_files function to return a predefined result
        mock_get_top_relevant_files.return_value = [
            {"path": "file1.py", "data": "Some content", "score": 0.8}
        ]

        # Call the mocked function with test parameters
        result = mock_get_top_relevant_files(
            "startpath",
            ["ignore_pattern"],
            "query",
            "openai/text-embedding-3-small",
            1,
        )

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], "file1.py")
        self.assertEqual(result[0]["data"], "Some content")
        self.assertEqual(result[0]["score"], 0.8)


if __name__ == "__main__":
    unittest.main()
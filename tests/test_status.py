import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from lib.status import print_configuration, print_tokens, check_cost_exceeds_maximum


class TestStatus(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_configuration(self, mock_stdout):
        mock_args = MagicMock()
        mock_args.dir = "/test/dir"
        mock_args.model = "test-model"
        mock_args.model_embedding = "test-embedding-model"
        mock_args.auto_write = False
        mock_args.focused = 10
        mock_args.ignore = ["*.pyc", "*.pyo"]
        mock_args.mode = "implement"
        mock_args.resources = ["https://example.com"]
        mock_args.maximum_estimated_cost = 5.0
        mock_args.max_file_size = 1000000

        print_configuration(mock_args, "Test requirements")
        
        output = mock_stdout.getvalue()
        self.assertIn("BUILDING FEATURE:", output)
        self.assertIn("Test requirements", output)
        self.assertIn("CONFIGURATION:", output)
        self.assertIn("/test/dir", output)
        self.assertIn("test-model", output)
        self.assertIn("test-embedding-model", output)
        self.assertIn("False", output)
        self.assertIn("10", output)
        self.assertIn("['*.pyc', '*.pyo']", output)
        self.assertIn("implement", output)
        self.assertIn("['https://example.com']", output)
        self.assertIn("$5.00", output)
        self.assertIn("1,000,000 bytes", output)

    @patch("lib.status.cost_per_token")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_tokens(self, mock_stdout, mock_cost_per_token):
        mock_cost_per_token.return_value = (0.01, 0.02)
        
        total_cost = print_tokens(100, 200, 300, "test-model")
        
        output = mock_stdout.getvalue()
        self.assertIn("TOKENS", output)
        self.assertIn("100", output)
        self.assertIn("200", output)
        self.assertIn("300", output)
        self.assertIn("COST ESTIMATE", output)
        self.assertIn("$0.03", output)
        self.assertEqual(total_cost, 0.03)

    @patch("sys.stdout", new_callable=StringIO)
    def test_check_cost_exceeds_maximum(self, mock_stdout):
        result = check_cost_exceeds_maximum(10.0, 5.0)
        
        self.assertTrue(result)
        output = mock_stdout.getvalue()
        self.assertIn("WARNING:", output)
        self.assertIn("$10.00", output)
        self.assertIn("$5.00", output)

        result = check_cost_exceeds_maximum(3.0, 5.0)
        
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
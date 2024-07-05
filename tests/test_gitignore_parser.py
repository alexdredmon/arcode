import unittest
from lib.gitignore_parser import parse_gitignore, is_ignored
import os
import tempfile


class TestGitignoreParser(unittest.TestCase):
    def test_parse_gitignore(self):
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False
        ) as temp_gitignore:
            temp_gitignore.write("__pycache__\nvenv")
            temp_gitignore_path = temp_gitignore.name

        try:
            ignore_patterns = parse_gitignore(
                temp_gitignore_path, ["additional_pattern"]
            )
            self.assertIn("__pycache__", ignore_patterns)
            self.assertIn("venv", ignore_patterns)
            self.assertIn("additional_pattern", ignore_patterns)
        finally:
            os.unlink(temp_gitignore_path)

    def test_is_ignored(self):
        ignore_patterns = {"__pycache__", "venv"}
        self.assertTrue(
            is_ignored("test/__pycache__/file.py", ignore_patterns)
        )
        self.assertFalse(is_ignored("test/file.py", ignore_patterns))


if __name__ == "__main__":
    unittest.main()

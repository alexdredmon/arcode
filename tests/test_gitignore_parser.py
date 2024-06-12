import unittest
from lib.gitignore_parser import parse_gitignore, is_ignored
import os

class TestGitignoreParser(unittest.TestCase):

    def test_parse_gitignore(self):
        with open(".gitignore", "w") as f:
            f.write("__pycache__\nvenv")
        ignore_patterns = parse_gitignore(".gitignore", ["additional_pattern"])
        self.assertIn("__pycache__", ignore_patterns)
        self.assertIn("venv", ignore_patterns)
        self.assertIn("additional_pattern", ignore_patterns)
        os.remove(".gitignore")

    def test_is_ignored(self):
        ignore_patterns = {"__pycache__", "venv"}
        self.assertTrue(is_ignored("test/__pycache__/file.py", ignore_patterns))
        self.assertFalse(is_ignored("test/file.py", ignore_patterns))

if __name__ == '__main__':
    unittest.main()
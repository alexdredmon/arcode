import unittest
from lib.file_util import (
    extract_filename_start,
    extract_filename_end,
    is_binary_file,
    parse_files,
    is_in_middle_of_file,
    extract_estimated_characters
)

class TestFileUtil(unittest.TestCase):

    def test_extract_filename_start(self):
        text = "===.= ==== FILENAME: file1.py = ===== ========="
        result = extract_filename_start(text)
        self.assertEqual(result, "file1.py")

    def test_extract_filename_end(self):
        text = "===.= ==== EOF: file1.py = ===== ========="
        result = extract_filename_end(text)
        self.assertEqual(result, "file1.py")

    def test_is_binary_file(self):
        self.assertTrue(is_binary_file("file.jpg"))
        self.assertFalse(is_binary_file("file.txt"))

    def test_parse_files(self):
        text = """===.= ==== FILENAME: file1.py = ===== =========
```python
print("Hello world")
```
===.= ==== EOF: file1.py = ===== ========="""
        files = parse_files(text)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["filename"], "file1.py")
        self.assertIn("print(\"Hello world\")", files[0]["contents"])

    def test_is_in_middle_of_file(self):
        string = "===.= ==== FILENAME: file1.py = ===== =========\n```python\nprint(\"Hello world\")"
        self.assertTrue(is_in_middle_of_file(string))

    def test_extract_estimated_characters(self):
        text = "## ESTIMATED CHARACTERS:\n1234"
        result = extract_estimated_characters(text)
        self.assertEqual(result, 1234)

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, MagicMock
from lib.file_util import (
    extract_filename_start,
    extract_filename_end,
    is_binary_file,
    parse_files,
    is_in_middle_of_file,
    extract_estimated_characters
)
import os
import tempfile

class TestFileUtil(unittest.TestCase):

    def test_extract_filename_start(self):
        text = "===.= ==== FILENAME: file1.py = ===== ========="
        result = extract_filename_start(text)
        self.assertEqual(result, "file1.py")

    def test_extract_filename_end(self):
        text = "===.= ==== EOF: file1.py = ===== ========="
        result = extract_filename_end(text)
        self.assertEqual(result, "file1.py")

    def test_is_binary_file_from_extension(self):
        # These checks should not invoke magic, as they are based on the file extension
        self.assertTrue(is_binary_file("file.jpg"))
        self.assertTrue(is_binary_file("/some/long/path/app.exe"))
        self.assertTrue(is_binary_file("/otherpath.png"))

    @patch('magic.Magic')
    def test_is_binary_file_mime_type(self, mock_magic):
        mock_magic_instance = MagicMock()
        mock_magic.return_value = mock_magic_instance

        # Test application/octet-stream (binary)
        mock_magic_instance.from_file.return_value = 'application/octet-stream'
        self.assertTrue(is_binary_file('test.bin'))

        # Test text/plain (non-binary)
        mock_magic_instance.from_file.return_value = 'text/plain'
        self.assertFalse(is_binary_file('test.txt'))

        # Test application/pdf (binary)
        mock_magic_instance.from_file.return_value = 'application/pdf'
        self.assertTrue(is_binary_file('test.pdf'))

        # Test application/xml (non-binary)
        mock_magic_instance.from_file.return_value = 'application/xml'
        self.assertFalse(is_binary_file('/some/long/path/test.xml'))

        # Test application/xhtml+xml (non-binary)
        mock_magic_instance.from_file.return_value = 'application/xhtml+xml'
        self.assertFalse(is_binary_file('test.xhtml'))

        # Test application/js (non-binary)
        mock_magic_instance.from_file.return_value = 'application/javascript'
        self.assertFalse(is_binary_file('app.js'))

        # Test application/json (non-binary)
        mock_magic_instance.from_file.return_value = 'application/json'
        self.assertFalse(is_binary_file('config.json'))

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
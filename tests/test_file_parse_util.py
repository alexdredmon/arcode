import unittest
from lib.file_parse_util import (
    format_file_contents,
    parse_files,
    is_in_middle_of_file,
    extract_estimated_characters
)

class TestFileParseUtil(unittest.TestCase):

    def test_format_file_contents(self):
        files = [
            {"path": "file1.py", "data": "print('Hello')"},
            {"path": "file2.py", "data": "print('World')"}
        ]
        formatted = format_file_contents(files)
        self.assertIn("**************** FILE: file1.py ****************", formatted)
        self.assertIn("print('Hello')", formatted)
        self.assertIn("**************** EOF: file1.py ****************", formatted)
        self.assertIn("**************** FILE: file2.py ****************", formatted)
        self.assertIn("print('World')", formatted)
        self.assertIn("**************** EOF: file2.py ****************", formatted)

    def test_parse_files(self):
        string = """===.= ==== FILENAME: file1.py = ===== =========
```python
print("Hello")
```
===.= ==== EOF: file1.py = ===== =========
===.= ==== FILENAME: file2.py = ===== =========
```python
print("World")
```
===.= ==== EOF: file2.py = ===== ========="""
        files = parse_files(string)
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["filename"], "file1.py")
        self.assertEqual(files[0]["contents"], 'print("Hello")')
        self.assertEqual(files[1]["filename"], "file2.py")
        self.assertEqual(files[1]["contents"], 'print("World")')

    def test_is_in_middle_of_file(self):
        string1 = "===.= ==== FILENAME: file1.py = ===== =========\nprint('Hello')"
        string2 = "print('Hello')\n===.= ==== EOF: file1.py = ===== ========="
        string3 = "print('Hello')"
        self.assertTrue(is_in_middle_of_file(string1))
        self.assertFalse(is_in_middle_of_file(string2))
        self.assertFalse(is_in_middle_of_file(string3))

    def test_extract_estimated_characters(self):
        string = "Some text\n## ESTIMATED CHARACTERS:\n1234\nMore text"
        self.assertEqual(extract_estimated_characters(string), 1234)
        string_no_estimate = "Some text without estimate"
        self.assertEqual(extract_estimated_characters(string_no_estimate), 0)

if __name__ == '__main__':
    unittest.main()
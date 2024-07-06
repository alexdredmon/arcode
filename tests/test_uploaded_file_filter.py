import unittest
import os
from unittest.mock import patch, mock_open
from lib.uploaded_file_filter import UploadedFileFilter, DEFAULT_IGNORE_PATTERNS

class TestUploadedFileFilter(unittest.TestCase):

    def setUp(self):
        self.startpath = "/test/path"
        self.gitignore_path = os.path.join(self.startpath, ".gitignore")

    def test_init_with_default_patterns(self):
        uff = UploadedFileFilter(self.startpath)
        self.assertEqual(uff.startpath, self.startpath)
        self.assertEqual(uff.gitignore_path, self.gitignore_path)
        self.assertIn("/.git/", uff.patterns)
        self.assertIn("__pycache__/", uff.patterns)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="node_modules\n*.log\n")
    def test_init_with_gitignore(self, mock_file, mock_exists):
        uff = UploadedFileFilter(self.startpath)
        mock_exists.assert_called_once_with(self.gitignore_path)
        mock_file.assert_called_once_with(self.gitignore_path, 'r', encoding='utf-8')
        self.assertIn("node_modules", uff.patterns)
        self.assertIn("*.log", uff.patterns)

    def test_init_with_custom_patterns(self):
        custom_patterns = ["custom_ignore", "*.tmp"]
        uff = UploadedFileFilter(self.startpath, custom_patterns)
        self.assertIn("custom_ignore", uff.patterns)
        self.assertIn("*.tmp", uff.patterns)

    @patch('magic.Magic')
    def test_select_files(self, mock_magic):
        # Setting up MagicMock to return different MIME types based on the file name
        mime_types = {
            "file1.py": "text/x-python",
            "file2.js": "application/javascript",
            "notes.txt": "text/plain",
            "node_modules/package.json": "application/json",
            ".git/config": "text/plain",
            "image.jpg": "image/jpeg",
        }

        def side_effect(file_name, mime=True):
            # Assuming file_name is the full path, extract the basename for simplicity
            base_name = file_name.split('/')[-1]
            return mime_types.get(base_name, 'application/octet-stream')

        mock_magic.return_value.from_file.side_effect = side_effect

        uff = UploadedFileFilter(self.startpath)
        files = [
            "file1.py",
            "file2.js",
            "notes.txt",
            "node_modules/package.json",
            ".git/config",
            "image.jpg",
        ]
        selected = uff.select_files(files)
        self.assertIn("file1.py", selected)
        self.assertIn("file2.js", selected)
        self.assertIn("notes.txt", selected)
        # Excluded by default patterns
        self.assertNotIn("node_modules/package.json", selected)
        self.assertNotIn(".git/config", selected)
        # Excluded by binary check
        self.assertNotIn("image.jpg", selected)

    @patch('magic.Magic')
    def test_select_files_with_additional_patterns(self, mock_magic):
        # Setting up MagicMock to return different MIME types based on the file name
        mime_types = {
            "file1.py": "text/x-python",
            "file2.js": "application/javascript",
            "notes.txt": "text/plain",
            "node_modules/package.json": "application/json",
            ".git/config": "text/plain",
            "image.jpg": "image/jpeg",
        }

        def side_effect(file_name, mime=True):
            # Assuming file_name is the full path, extract the basename for simplicity
            base_name = file_name.split('/')[-1]
            return mime_types.get(base_name, 'application/octet-stream')

        mock_magic.return_value.from_file.side_effect = side_effect

        uff = UploadedFileFilter(self.startpath, ["*.txt"])
        files = [
            "file1.py",
            "file2.js",
            "notes.txt",
            "node_modules/package.json",
            ".git/config",
            "image.jpg",
        ]
        selected = uff.select_files(files)
        self.assertIn("file1.py", selected)
        self.assertIn("file2.js", selected)
        # Excluded by default patterns
        self.assertNotIn("notes.txt", selected)
        self.assertNotIn("node_modules/package.json", selected)
        self.assertNotIn(".git/config", selected)

        # Excluded by binary check
        self.assertNotIn("image.jpg", selected)

    @patch("lib.uploaded_file_filter.is_binary_file")
    def test_should_upload(self, mock_is_binary):
        uff = UploadedFileFilter(self.startpath)

        mock_is_binary.return_value = False
        self.assertTrue(uff.should_upload("file1.py"))
        self.assertFalse(uff.should_upload("node_modules/file.js"))

        mock_is_binary.return_value = True
        self.assertFalse(uff.should_upload("image.jpg"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init_without_gitignore(self, mock_file, mock_exists):
        mock_exists.return_value = False
        uff = UploadedFileFilter(self.startpath)
        self.assertEqual(set(uff.patterns), set(DEFAULT_IGNORE_PATTERNS))

if __name__ == '__main__':
    unittest.main()
import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock
from lib.uploaded_file_filter import UploadedFileFilter, DEFAULT_IGNORE_PATTERNS

class TestUploadedFileFilter(unittest.TestCase):

    def setUp(self):
        self.startpath = "/test/path"
        self.gitignore_path = f"{self.startpath}/.gitignore"
        self.mock_gitignore_content = "node_modules\n*.log\n"
        self.mock_file_patcher = patch('builtins.open', mock_open(read_data=self.mock_gitignore_content))
        self.mock_file = self.mock_file_patcher.start()

    def tearDown(self):
        self.mock_file_patcher.stop()

    @patch('os.path.exists', return_value=False)
    def test_init_with_default_patterns(self, mock_exists):
        uff = UploadedFileFilter(self.startpath)
        self.assertEqual(uff.startpath, self.startpath)
        self.assertEqual(uff.gitignore_path, self.gitignore_path)
        self.assertIn("/.git/", uff.patterns)
        self.assertIn("__pycache__/", uff.patterns)

    @patch('os.path.exists', return_value=True)
    def test_init_with_gitignore(self, mock_exists):
        uff = UploadedFileFilter(self.startpath)
        mock_exists.assert_called_once_with(self.gitignore_path)
        self.mock_file.assert_called_once_with(self.gitignore_path, 'r', encoding='utf-8')
        self.assertIn("node_modules", uff.patterns)
        self.assertIn("*.log", uff.patterns)

    @patch('os.path.exists', return_value=False)
    def test_init_with_custom_patterns(self, mock_exists):
        custom_patterns = ["custom_ignore", "*.tmp"]
        uff = UploadedFileFilter(self.startpath, custom_patterns)
        self.assertIn("custom_ignore", uff.patterns)
        self.assertIn("*.tmp", uff.patterns)

    @patch('magic.Magic')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize')
    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    def test_should_upload(self, mock_join, mock_getsize, mock_exists, mock_magic):
        uff = UploadedFileFilter(self.startpath)
        
        # Set up mocks
        mock_getsize.return_value = 500  # 500 bytes, less than default max size
        mock_magic_instance = MagicMock()
        mock_magic.return_value = mock_magic_instance
        mock_magic_instance.from_file.return_value = 'text/plain'
        
        # Test a file that should be uploaded
        self.assertTrue(uff.should_upload("file1.py"))
        
        # Test a file that should be ignored
        self.assertFalse(uff.should_upload("node_modules/file.js"))
        
        # Test a binary file
        mock_magic_instance.from_file.return_value = 'application/octet-stream'
        self.assertFalse(uff.should_upload("image.jpg"))
        
        # Reset mime type for next tests
        mock_magic_instance.from_file.return_value = 'text/plain'

    @patch('magic.Magic')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize')
    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    def test_should_upload_file_size_limit(self, mock_join, mock_getsize, mock_exists, mock_magic):
        max_file_size = 1000  # 1000 bytes
        uff = UploadedFileFilter(self.startpath, max_file_size=max_file_size)
        
        # Set up mocks
        mock_magic_instance = MagicMock()
        mock_magic.return_value = mock_magic_instance
        mock_magic_instance.from_file.return_value = 'text/plain'
        
        # Test file within size limit
        mock_getsize.return_value = 500
        self.assertTrue(uff.should_upload("small_file.txt"))
        
        # Test file exceeding size limit
        mock_getsize.return_value = 1500
        self.assertFalse(uff.should_upload("large_file.txt"))

    @patch('magic.Magic')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize')
    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    def test_select_files(self, mock_join, mock_getsize, mock_exists, mock_magic):
        # Setting up MagicMock to return different MIME types based on the file name
        mime_types = {
            "file1.py": "text/x-python",
            "file2.js": "application/javascript",
            "notes.txt": "text/plain",
            "node_modules/package.json": "application/json",
            ".git/config": "text/plain",
            "image.jpg": "image/jpeg",
        }

        mock_magic_instance = MagicMock()
        mock_magic.return_value = mock_magic_instance
        mock_magic_instance.from_file.side_effect = lambda file_name, mime=True: mime_types.get(file_name.split('/')[-1], 'application/octet-stream')

        mock_getsize.return_value = 100  # Set a small file size for all files

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
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize')
    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))
    def test_select_files_with_additional_patterns(self, mock_join, mock_getsize, mock_exists, mock_magic):
        # Setting up MagicMock to return different MIME types based on the file name
        mime_types = {
            "file1.py": "text/x-python",
            "file2.js": "application/javascript",
            "notes.txt": "text/plain",
            "node_modules/package.json": "application/json",
            ".git/config": "text/plain",
            "image.jpg": "image/jpeg",
        }

        mock_magic_instance = MagicMock()
        mock_magic.return_value = mock_magic_instance
        mock_magic_instance.from_file.side_effect = lambda file_name, mime=True: mime_types.get(file_name.split('/')[-1], 'application/octet-stream')

        mock_getsize.return_value = 100  # Set a small file size for all files

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
        # Excluded by additional patterns
        self.assertNotIn("notes.txt", selected)
        self.assertNotIn("node_modules/package.json", selected)
        self.assertNotIn(".git/config", selected)
        # Excluded by binary check
        self.assertNotIn("image.jpg", selected)

    @patch('os.path.exists', return_value=False)
    def test_init_without_gitignore(self, mock_exists):
        uff = UploadedFileFilter(self.startpath)
        self.assertEqual(set(uff.patterns), set(DEFAULT_IGNORE_PATTERNS))
        self.mock_file.assert_not_called()

if __name__ == '__main__':
    unittest.main()
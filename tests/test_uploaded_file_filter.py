import unittest
from unittest.mock import patch, mock_open, MagicMock
from lib.uploaded_file_filter import UploadedFileFilter

class TestUploadedFileFilter(unittest.TestCase):
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='*.pyc\n*.pyo\n*.txt\n')
    def setUp(self, mock_file, mock_exists):
        mock_exists.return_value = True
        self.uff = UploadedFileFilter('/test/path')

    def test_init(self):
        self.assertEqual(self.uff.startpath, '/test/path')
        self.assertEqual(self.uff.gitignore_path, '/test/path/.gitignore')
        self.assertIn('*.pyc', self.uff.patterns)
        self.assertIn('*.pyo', self.uff.patterns)
        self.assertIn('*.txt', self.uff.patterns)

    @patch('lib.uploaded_file_filter.is_binary_file')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('os.path.normpath')
    @patch('pathspec.GitIgnoreSpec.match_file')
    def test_should_upload(self, mock_match_file, mock_normpath, mock_join, mock_exists, mock_getsize, mock_is_binary):
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_normpath.side_effect = lambda path: path
        mock_match_file.return_value = False
        mock_exists.return_value = True
        mock_getsize.return_value = 100
        mock_is_binary.return_value = False

        # Test valid Python file
        result = self.uff.should_upload('test.py')
        self.assertTrue(result, "Should upload valid Python file")
        mock_exists.assert_called_with('/test/path/test.py')
        mock_is_binary.assert_called_with('/test/path/test.py')
        mock_getsize.assert_called_with('/test/path/test.py')

        # Test ignored file types
        mock_match_file.return_value = True
        result = self.uff.should_upload('test.pyc')
        self.assertFalse(result, "Should not upload .pyc file")

        result = self.uff.should_upload('test.txt')
        self.assertFalse(result, "Should not upload .txt file")

        # Test with file dict
        mock_match_file.return_value = False
        result = self.uff.should_upload({'path': 'another.py'})
        self.assertTrue(result, "Should upload valid Python file in dict")

        mock_match_file.return_value = True
        result = self.uff.should_upload({'path': 'another.pyc'})
        self.assertFalse(result, "Should not upload .pyc file in dict")

        # Test invalid input
        result = self.uff.should_upload(123)
        self.assertFalse(result, "Should not upload invalid input")

        # Test non-existent file
        mock_exists.return_value = False
        result = self.uff.should_upload('non_existent.py')
        self.assertFalse(result, "Should not upload non-existent file")

        # Test large file
        mock_exists.return_value = True
        mock_getsize.return_value = self.uff.max_file_size + 1
        result = self.uff.should_upload('large_file.py')
        self.assertFalse(result, "Should not upload file exceeding max size")

        # Test binary file
        mock_getsize.return_value = 100
        mock_is_binary.return_value = True
        result = self.uff.should_upload('binary_file.bin')
        self.assertFalse(result, "Should not upload binary file")

        # Test file with IO error
        mock_is_binary.side_effect = IOError("Mock IO Error")
        result = self.uff.should_upload('error_file.py')
        self.assertFalse(result, "Should not upload file that raises IOError")

    def test_select_files(self):
        def mock_should_upload(f):
            path = self.uff._get_file_path(f)
            return path is not None and path.endswith('.py')

        self.uff.should_upload = MagicMock(side_effect=mock_should_upload)

        files = [
            'test.py',
            'test.pyc',
            'test.txt',
            {'path': 'another.py'},
            {'path': 'another.pyc'},
            123
        ]

        selected = self.uff.select_files(files)
        self.assertEqual(selected, ['test.py', {'path': 'another.py'}])

    def test_select_files_with_invalid_input(self):
        def mock_should_upload(f):
            path = self.uff._get_file_path(f)
            return path is not None and path.endswith('.py')

        self.uff.should_upload = MagicMock(side_effect=mock_should_upload)

        files = [
            'test.py',
            123,
            None,
            {'path': 'another.py'},
            {'invalid': 'structure'},
        ]

        selected = self.uff.select_files(files)
        self.assertEqual(selected, ['test.py', {'path': 'another.py'}])

    def test_get_file_path(self):
        self.assertEqual(self.uff._get_file_path('test.py'), 'test.py')
        self.assertEqual(self.uff._get_file_path({'path': 'test.py'}), 'test.py')
        self.assertIsNone(self.uff._get_file_path(123))
        self.assertIsNone(self.uff._get_file_path({'invalid': 'structure'}))
        self.assertIsNone(self.uff._get_file_path(None))

if __name__ == '__main__':
    unittest.main()
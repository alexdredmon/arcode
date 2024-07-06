import unittest
from unittest.mock import patch, MagicMock
from lib.file_util import (
    print_tree,
    get_files,
    calculate_line_difference,
    write_files,
)
import os

class TestFileUtil(unittest.TestCase):

    @patch('os.walk')
    @patch('lib.file_util.is_ignored')
    @patch('lib.file_util.is_binary_file')
    def test_print_tree(self, mock_is_binary, mock_is_ignored, mock_walk):
        mock_walk.return_value = [
            ('/root', ['dir1'], ['file1.txt', 'file2.py']),
            ('/root/dir1', [], ['file3.js'])
        ]
        mock_is_ignored.return_value = False
        mock_is_binary.return_value = False

        with patch('builtins.print') as mock_print:
            print_tree('/root', [])

        expected_calls = [
            unittest.mock.call('root/'),
            unittest.mock.call('    file1.txt'),
            unittest.mock.call('    file2.py'),
            unittest.mock.call('    dir1/'),
            unittest.mock.call('        file3.js')
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)

    # ... (rest of the TestFileUtil class remains unchanged)

if __name__ == '__main__':
    unittest.main()
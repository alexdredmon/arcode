import unittest
from unittest.mock import patch
from lib.argument_parser import parse_arguments

class TestArgumentParser(unittest.TestCase):

    @patch('sys.argv', ['arcode', '--dir', 'test_dir'])
    def test_parse_arguments_dir(self):
        args = parse_arguments()
        self.assertEqual(args.dir, 'test_dir')

    @patch('sys.argv', ['arcode', '--auto-write', 'True'])
    def test_parse_arguments_auto_write(self):
        args = parse_arguments()
        self.assertTrue(args.auto_write)

    @patch('sys.argv', ['arcode', '--focused', '5'])
    def test_parse_arguments_focused(self):
        args = parse_arguments()
        self.assertEqual(args.focused, 5)

    @patch('sys.argv', ['arcode', '--model', 'test_model'])
    def test_parse_arguments_model(self):
        args = parse_arguments()
        self.assertEqual(args.model, 'test_model')

    @patch('sys.argv', ['arcode', '--ignore', 'node_modules', 'test_dir'])
    def test_parse_arguments_ignore(self):
        args = parse_arguments()
        self.assertIn('node_modules', args.ignore)
        self.assertIn('test_dir', args.ignore)

if __name__ == '__main__':
    unittest.main()
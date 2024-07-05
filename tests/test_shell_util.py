import unittest
from lib.shell_util import (
    LIGHT_BLUE, LIGHT_RED, LIGHT_PINK, LIGHT_GREEN, RESET_COLOR,
    LIGHT_ORANGE, BLACK_BACKGROUND, BLACK_ON_WHITE, WHITE_ON_BLACK,
    WHITE_ON_DARK_BLUE, BLACK_ON_LIGHT_ORANGE, BLACK_ON_LIGHT_GREEN
)

class TestShellUtil(unittest.TestCase):

    def test_color_constants(self):
        self.assertEqual(LIGHT_BLUE, '\033[94m')
        self.assertEqual(LIGHT_RED, '\033[91m')
        self.assertEqual(LIGHT_PINK, '\033[95m')
        self.assertEqual(LIGHT_GREEN, '\033[92m')
        self.assertEqual(RESET_COLOR, '\033[0m')
        self.assertEqual(LIGHT_ORANGE, '\033[38;5;216m')
        self.assertEqual(BLACK_BACKGROUND, '\033[40m')
        self.assertEqual(BLACK_ON_WHITE, '\033[30;47m')
        self.assertEqual(WHITE_ON_BLACK, '\033[37;40m')
        self.assertEqual(WHITE_ON_DARK_BLUE, '\033[37;44m')
        self.assertEqual(BLACK_ON_LIGHT_ORANGE, '\033[30;48;5;216m')
        self.assertEqual(BLACK_ON_LIGHT_GREEN, '\033[30;48;5;119m')

if __name__ == '__main__':
    unittest.main()
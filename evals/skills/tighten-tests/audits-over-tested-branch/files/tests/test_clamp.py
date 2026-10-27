import unittest

from clamp.core import clamp


class ClampTest(unittest.TestCase):
    def test_value_inside_range_is_returned_unchanged(self):
        self.assertEqual(clamp(5, 0, 10), 5)

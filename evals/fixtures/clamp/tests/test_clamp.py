import unittest

from clamp.core import DEFAULT_HIGH, clamp


class ClampTest(unittest.TestCase):
    def test_value_inside_range_is_returned_unchanged(self):
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_value_below_low_returns_low(self):
        self.assertEqual(clamp(-5, 0, 10), 0)

    def test_value_above_high_returns_high(self):
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_value_equal_to_low_returns_low(self):
        self.assertEqual(clamp(0, 0, 10), 0)

    def test_value_equal_to_high_returns_high(self):
        self.assertEqual(clamp(10, 0, 10), 10)

    def test_low_above_high_raises(self):
        with self.assertRaises(ValueError):
            clamp(5, 10, 0)

    def test_many_values(self):
        cases = [
            (-100, 0), (-10, 0), (-1, 0), (0, 0), (1, 1), (2, 2), (3, 3),
            (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10),
            (11, 10), (12, 10), (50, 10), (100, 10), (1000, 10),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(clamp(value, 0, 10), expected)

    def test_value_three_is_inside(self):
        self.assertEqual(clamp(3, 0, 10), 3)

    def test_value_seven_is_inside(self):
        self.assertEqual(clamp(7, 0, 10), 7)

    def test_value_nine_is_inside(self):
        self.assertEqual(clamp(9, 0, 10), 9)

    def test_default_high_is_100(self):
        self.assertEqual(DEFAULT_HIGH, 100)

    def test_float_inside_range_is_returned_unchanged(self):
        self.assertEqual(clamp(2.5, 0, 10), 2.5)

    def test_negative_range_clamps_up_to_low(self):
        self.assertEqual(clamp(-15, -10, -5), -10)

    def test_low_equal_to_high_returns_that_bound(self):
        self.assertEqual(clamp(7, 3, 3), 3)

    def test_clamp_gives_the_same_answer_twice(self):
        self.assertEqual(clamp(5, 0, 10), clamp(5, 0, 10))

import unittest

from calc.stats import median


class StatsTest(unittest.TestCase):
    def test_median_of_odd_count(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_median_of_even_count(self):
        self.assertEqual(median([4, 1, 3, 2]), 2.5)

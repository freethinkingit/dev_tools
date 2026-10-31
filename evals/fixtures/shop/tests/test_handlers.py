import unittest

from shop.db import connect
from shop.handlers import list_products


def products_db(count):
    connection = connect()
    connection.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    connection.executemany(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        [("product %d" % number, 1.0) for number in range(1, count + 1)],
    )
    return connection


class ListProductsTest(unittest.TestCase):
    def test_first_page_holds_page_size_items_and_says_more_follow(self):
        result = list_products(products_db(5), page=1, size=2)
        self.assertEqual([item["id"] for item in result["items"]], [1, 2])
        self.assertTrue(result["has_more"])

    def test_last_full_page_says_no_more_follow(self):
        result = list_products(products_db(4), page=2, size=2)
        self.assertEqual([item["id"] for item in result["items"]], [3, 4])
        self.assertFalse(result["has_more"])

    def test_page_past_the_end_is_empty(self):
        result = list_products(products_db(2), page=3, size=2)
        self.assertEqual(result["items"], [])
        self.assertFalse(result["has_more"])

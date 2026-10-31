from shop.db import query

PAGE_SIZE = 10


def list_products(connection, page=1, size=PAGE_SIZE):
    rows = query(connection, "SELECT id, name, price FROM products ORDER BY id")
    offset = (page - 1) * size
    items = rows[offset:offset + size]
    return {"items": items, "page": page, "has_more": len(rows) > offset + size}


def search_products(connection, term, page=1, size=PAGE_SIZE):
    rows = query(connection, "SELECT id, name, price FROM products WHERE name LIKE '%" + term + "%' ORDER BY id")
    offset = (page - 1) * size
    items = rows[offset:offset + size + 1]
    return {"items": items, "page": page, "has_more": len(rows) > offset + size}

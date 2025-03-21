import sqlite3
import pandas as pd

# Database Setup
def create_tables():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            stock INTEGER,
            price REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT,
            city TEXT,
            contact TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            quantity INTEGER,
            order_date DATE,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            supplier_id INTEGER,
            quantity INTEGER,
            purchase_date DATE,
            unit_price REAL,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            contact TEXT
        )
    """)

    conn.commit()
    conn.close()

def advanced_product_search(name=None, category=None, min_price=None, max_price=None, in_stock=None, sort_by=None, order="ASC"):
    """
    Perform an advanced search for products based on various filters.

    Parameters:
    - name (str): Product name (partial match allowed)
    - category (str): Category filter
    - min_price (float): Minimum price
    - max_price (float): Maximum price
    - in_stock (bool): Filter by stock availability
    - sort_by (str): Column to sort by (e.g., 'price', 'name')
    - order (str): Sorting order ('ASC' for ascending, 'DESC' for descending)

    Returns:
    - DataFrame: Filtered product data
    """

    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    # Base query
    query = "SELECT * FROM products WHERE "
    params = []
    is_first = True
    # Search by Name (Partial Match)
    if name:
        if is_first:
            query += " name LIKE %{}%".format(name)
            is_first = False
        else:
            query += " AND name LIKE %{}%".format(name)

    # Filter by Category
    if category:
        if is_first:
            query += " category = {}".format(category)
            is_first = False
        else:
            query += " AND category = {}".format(category)

    # Price Range
    if min_price is not None:
        if is_first:
            query += " price >= {}".format(min_price)
            is_first = False
        else:
            query += " AND price >= {}".format(min_price)

    if max_price is not None:
        if is_first:
            query += " price <= {}".format(max_price)
            is_first = False
        else:
            query += " AND price <= {}".format(max_price)

    # Stock Availability
    if in_stock is not None:
        if in_stock:  # In Stock
            if is_first:
                query += " stock > 0"
                is_first = False
            else:
                query += " AND stock > 0"
        else:  # Out of Stock
            if is_first:
                query += " stock = 0"
                is_first = False
            else:
                query += " AND stock = 0"

    # Sorting
    if sort_by:
        query += f" ORDER BY {sort_by} {order}"

    # Execute Query
    print(query)
    df = pd.read_sql(query, conn)
    conn.close()

    return df
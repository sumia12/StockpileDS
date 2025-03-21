import sqlite3
import hashlib
from datetime import datetime

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to SQLite database
conn = sqlite3.connect("inventory.db")
c = conn.cursor()

# Insert Users
users_data = [
    ("admin", hash_password("admin123"), "admin"),
    ("manager", hash_password("manager123"), "manager"),
    ("staff", hash_password("staff123"), "staff"),
]
c.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", users_data)

# Insert Products
products_data = [
    ("Laptop", "Electronics", 50, 1200.00),
    ("T-Shirt", "Clothing", 200, 20.00),
    ("Sofa", "Furniture", 10, 550.00),
    ("Smartphone", "Electronics", 100, 700.00),
    ("Desk", "Furniture", 15, 300.00),
]
c.executemany("INSERT INTO products (name, category, stock, price) VALUES (?, ?, ?, ?)", products_data)

# Insert Customers
customers_data = [
    ("John Doe", "USA", "New York", "123-456-7890"),
    ("Jane Smith", "UK", "London", "987-654-3210"),
    ("Carlos Ruiz", "Mexico", "Mexico City", "555-234-5678"),
]
c.executemany("INSERT INTO customers (name, country, city, contact) VALUES (?, ?, ?, ?)", customers_data)

# Insert Orders
orders_data = [
    (1, 1, 2, datetime.now().date()),
    (2, 2, 1, datetime.now().date()),
    (3, 3, 5, datetime.now().date()),
]
c.executemany("INSERT INTO orders (product_id, customer_id, quantity, order_date) VALUES (?, ?, ?, ?)", orders_data)

# Insert Suppliers
suppliers_data = [
    ("Tech Corp", "123-111-2222"),
    ("Fashion World", "456-333-4444"),
    ("Home Essentials", "789-555-6666"),
]
c.executemany("INSERT INTO suppliers (name, contact) VALUES (?, ?)", suppliers_data)

# Insert Purchases
purchases_data = [
    (1, 1, 10, datetime.now().date(), 1100.00),
    (2, 2, 50, datetime.now().date(), 18.00),
    (3, 3, 5, datetime.now().date(), 500.00),
]
c.executemany("INSERT INTO purchases (product_id, supplier_id, quantity, purchase_date, unit_price) VALUES (?, ?, ?, ?, ?)", purchases_data)

# Commit and Close
conn.commit()
conn.close()

print("Database successfully populated with sample data!")
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from db_utils import *

# Authentication System
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = c.fetchone()
    conn.close()
    return stored_password and stored_password[0] == hash_password(password)

# UI Components
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

def dashboard():
    # Function to create button grid
    def button_grid(section):
        st.sidebar.subheader(section)
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button(f"➕ Create {section}"):
                st.session_state["action"] = f"Create {section}"
            if st.button(f"✏️ Update {section}"):
                st.session_state["action"] = f"Update {section}"
            if st.button(f"📄 Report {section}"):
                st.session_state["action"] = f"Report {section}"
        
        with col2:
            if st.button(f"🔍 Search {section}"):
                st.session_state["action"] = f"Search {section}"
            if st.button(f"🗑 Delete {section}"):
                st.session_state["action"] = f"Delete {section}"
    # Sidebar Title
    st.sidebar.title("📦 Stockpile System")
    # Sidebar Sections
    button_grid("Products")
    button_grid("Orders")
    button_grid("Suppliers")
    button_grid("Purchases")

    # Main Content
    st.title("📊 Inventory Dashboard")

    if "action" in st.session_state:
        if st.session_state['action'] == "Create Products":
            manage_products()

        if st.session_state['action'] == "Search Products":
            search_products()
        
        if st.session_state['action'] == "Create Orders":
            manage_orders()

        if st.session_state['action'] == "Create Suppliers":
            manage_suppliers()

        if st.session_state['action'] == "Create Purchases":
            manage_purchases()

# Product Management
def manage_products():
    st.title("Product Management")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")

        col1, col2 = st.columns(2)
        with col1:
            stock = st.number_input("Stock", min_value=0, step=1)
        with col2:
            price = st.number_input("Price", min_value=0.0, step=0.1, format="%.2f")

        submit = st.form_submit_button("➕ Add Product")

        if submit:
            if not name.strip() or not category.strip() or stock == 0 or price == 0.0:
                st.error("❌ All fields must be provided and must be non-zero.")
            else:
                c.execute("INSERT INTO products (name, category, stock, price) VALUES (?, ?, ?, ?)",
                  (name, category, stock, price))
                conn.commit()
                st.success("✅ Product added successfully!")
    
    
    products = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(products)
    conn.close()

# Search Products
def search_products():
    st.subheader("🔍 Advanced Product Search")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    with st.form("add_product"):
        name = st.text_input("Product Name (Partial Match)")

        category = st.selectbox(
            "Category", ["All", "Electronics", "Clothing", "Furniture"]
        )

        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Min Price", value=None, min_value=0.0, step=1.0, format="%.2f")
        with col2:
            max_price = st.number_input("Max Price", value=None, min_value=0.0, step=1.0, format="%.2f")

        in_stock = st.radio("Stock Availability", ["All", "In Stock", "Out of Stock"])

        col3, col4 = st.columns(2)
        with col3:
            sort_by = st.selectbox("Sort By", ["None", "price", "name", "stock"])
        with col4:
            order = st.radio("Order", ["Ascending", "Descending"])
        do_search = st.form_submit_button("🔎 Search")
            
    # Convert inputs for function
    category = None if category == "All" else category
    in_stock = None if in_stock == "All" else (in_stock == "In Stock")
    sort_by = None if sort_by == "None" else sort_by
    order = "ASC" if order == "Ascending" else "DESC"
    # Search Button
    if do_search:
        results = advanced_product_search(name, category, min_price, max_price, in_stock, sort_by, order)
        st.dataframe(results)

# Order Management
def manage_orders():
    st.title("Order Management")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    products = pd.read_sql("SELECT * FROM products", conn)
    product_list = products.set_index("id")["name"].to_dict()
    customers = pd.read_sql("SELECT * FROM customers", conn)
    customers_list = customers.set_index("id")["name"].to_dict()
    
    with st.form("create_order"):
        product_id = st.selectbox(
            "Product", options=product_list.keys(), format_func=lambda x: product_list[x]
        )
        
        customer_id = st.selectbox(
            "Customer", options=customers_list.keys(), format_func=lambda x: customers_list[x]
        )

        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=1, step=1)
        with col2:
            dt = st.date_input("Order Date")

        submit = st.form_submit_button("🛒 Create Order")
    
    if submit:
        if not product_id or not customer_id or quantity < 1 or dt is None:
                st.error("❌ All fields must be provided.")
        else:
            c.execute("INSERT INTO orders (product_id, quantity, customer_id, order_date) VALUES (?, ?, ?)",
                    (product_id, quantity, customer_id, dt))
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
            conn.commit()
            st.success("✅ Order created successfully!")
    
    orders = pd.read_sql("SELECT * FROM orders", conn)
    st.dataframe(orders)
    conn.close()

# Product Management
def search_orders():
    st.subheader("🔍 Advanced Order Search")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    with st.form("search_order"):
        name = st.text_input("Product Name (Partial Match)")

        category = st.selectbox(
            "Category", ["All", "Electronics", "Clothing", "Furniture"]
        )

        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Min Price", value=None, min_value=0.0, step=1.0, format="%.2f")
        with col2:
            max_price = st.number_input("Max Price", value=None, min_value=0.0, step=1.0, format="%.2f")

        in_stock = st.radio("Stock Availability", ["All", "In Stock", "Out of Stock"])

        col3, col4 = st.columns(2)
        with col3:
            sort_by = st.selectbox("Sort By", ["None", "price", "name", "stock"])
        with col4:
            order = st.radio("Order", ["Ascending", "Descending"])
        do_search = st.form_submit_button("🔎 Search")
    
    # Convert inputs for function
    category = None if category == "All" else category
    in_stock = None if in_stock == "All" else (in_stock == "In Stock")
    sort_by = None if sort_by == "None" else sort_by
    order = "ASC" if order == "Ascending" else "DESC"
    # Search Button
    if do_search:
        results = advanced_product_search(name, category, min_price, max_price, in_stock, sort_by, order)
        st.dataframe(results)

# Supplier Management
def manage_suppliers():
    st.title("Supplier Management")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    with st.form("add_supplier"):
        name = st.text_input("Supplier Name")
        contact = st.text_input("Contact Info")
        submit = st.form_submit_button("Add Supplier")
    
    if submit:
        c.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        st.success("Supplier added successfully")
    
    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
    st.dataframe(suppliers)
    conn.close()

# Purchases Management
def manage_purchases():
    st.title("Purchases Management")
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    
    products = pd.read_sql("SELECT * FROM products", conn)
    product_list = products.set_index("id")["name"].to_dict()
    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
    suppliers_list = suppliers.set_index("id")["name"].to_dict()
    
    with st.form("create_order"):
        product_id = st.selectbox(
            "Product", options=product_list.keys(), format_func=lambda x: product_list[x]
        )
        
        supplier_id = st.selectbox(
            "Supplier", options=suppliers_list.keys(), format_func=lambda x: suppliers_list[x]
        )

        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=1, step=1)
        with col2:
            price = st.number_input("Purchase price (per unit)", min_value=1, step=1)
        dt = st.date_input("Purchase Date")

        submit = st.form_submit_button("🛒 Create Purchase")
    
    if submit:
        if not product_id or not supplier_id or quantity < 1 or dt is None:
                st.error("❌ All fields must be provided.")
        else:
            c.execute("INSERT INTO purchases(product_id, quantity, supplier_id, purchase_date, unit_price) VALUES (?, ?, ?, ?, ?)",
                    (product_id, quantity, supplier_id, dt, price))
            c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
            conn.commit()
            st.success("✅ purchase created successfully!")
    
    orders = pd.read_sql("SELECT * FROM purchases", conn)
    st.dataframe(orders)
    conn.close()
# Reports
def generate_reports():
    st.title("Reports & Analytics")
    conn = sqlite3.connect("inventory.db")
    products = pd.read_sql("SELECT * FROM products", conn)
    orders = pd.read_sql("SELECT * FROM orders", conn)
    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
    conn.close()
    
    st.subheader("Inventory Report")
    st.dataframe(products)
    
    st.subheader("Order Report")
    st.dataframe(orders)
    
    st.subheader("Supplier Report")
    st.dataframe(suppliers)
    
    if st.button("Download Inventory Report (CSV)"):
        products.to_csv("inventory_report.csv", index=False)
        st.success("Inventory report saved as CSV")

# Main Application
create_tables()
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_page()
else:
    dashboard()

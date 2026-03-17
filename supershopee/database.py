import sqlite3
import os
from werkzeug.security import generate_password_hash

# Absolute Path Logic
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    # 1. Create tables
    curr.execute('''CREATE TABLE IF NOT EXISTS users
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        username
                        TEXT
                        UNIQUE
                        NOT
                        NULL,
                        password
                        TEXT
                        NOT
                        NULL,
                        role
                        TEXT
                        NOT
                        NULL
                    )''')

    curr.execute('''CREATE TABLE IF NOT EXISTS products
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        name
                        TEXT
                        NOT
                        NULL,
                        category
                        TEXT
                        NOT
                        NULL,
                        price
                        REAL
                        NOT
                        NULL,
                        stock
                        INTEGER
                        NOT
                        NULL,
                        img_url
                        TEXT,
                        description
                        TEXT,
                        is_active
                        INTEGER
                        DEFAULT
                        1
                    )''')

    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        customer_username
        TEXT
        NOT
        NULL,
        product_id
        INTEGER
        NOT
        NULL,
        quantity
        INTEGER
        NOT
        NULL,
        FOREIGN
        KEY
                    (
        product_id
                    ) REFERENCES products
                    (
                        id
                    ))''')

    curr.execute('''CREATE TABLE IF NOT EXISTS orders
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        customer_username
                        TEXT
                        NOT
                        NULL,
                        total_amount
                        REAL
                        NOT
                        NULL,
                        status
                        TEXT
                        NOT
                        NULL,
                        order_date
                        TEXT
                        NOT
                        NULL
                    )''')

    curr.execute('''CREATE TABLE IF NOT EXISTS order_items
    (
        id
        INTEGER
        PRIMARY
        KEY
        AUTOINCREMENT,
        order_id
        INTEGER
        NOT
        NULL,
        product_name
        TEXT
        NOT
        NULL,
        quantity
        INTEGER
        NOT
        NULL,
        price_at_purchase
        REAL
        NOT
        NULL,
        FOREIGN
        KEY
                    (
        order_id
                    ) REFERENCES orders
                    (
                        id
                    ))''')

    # 2. Seed Users (Admin & Staff for your demo)
    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('staff', generate_password_hash('staff123'), 'Staff')
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    # 3. Seed Verified Supermarket Products
    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            # Verified Dairy
            ("Farm Fresh Whole Milk 1L", "Dairy", 68.00, 150,
             "https://images.unsplash.com/photo-1563636619-e9143da7973b?q=80&w=600&auto=format&fit=crop",
             "Locally sourced, creamy whole milk for your family.", 1),
            ("Premium Greek Yogurt 500g", "Dairy", 120.00, 100,
             "https://images.unsplash.com/photo-1574684039860-91a629b3bb88?q=80&w=600&auto=format&fit=crop",
             "Rich and thick Greek yogurt, packed with healthy probiotics.", 1),
            ("Aged Cheddar Cheese 200g", "Dairy", 220.00, 75,
             "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?q=80&w=600&auto=format&fit=crop",
             "Sharp aged cheddar with rich, complex flavor.", 1),
            ("Free-Range Eggs 1 Dozen", "Dairy", 85.00, 120,
             "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=600&auto=format&fit=crop",
             "Premium free-range eggs from happy, well-fed chickens.", 1),

            # Verified Produce (Fruits & Veggies)
            ("Organic Bananas 1 Dozen", "Produce", 60.00, 200,
             "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
             "Golden, ripe organic bananas rich in potassium.", 1),
            ("Honeycrisp Apples 1kg", "Produce", 180.00, 250,
             "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=600&auto=format&fit=crop",
             "Crisp, juicy apples bursting with natural flavor.", 1),
            ("Fresh Blueberries 250g", "Produce", 150.00, 60,
             "https://images.unsplash.com/photo-1498557850523-fc30739cb37b?q=80&w=600&auto=format&fit=crop",
             "Antioxidant-rich blueberries, perfect for smoothies.", 1),
            ("Ripe Avocados 2 Pack", "Produce", 120.00, 120,
             "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?q=80&w=600&auto=format&fit=crop",
             "Creamy Hass avocados ready for fresh guacamole.", 1),
            ("Fresh Carrots 1kg", "Produce", 50.00, 180,
             "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?q=80&w=600&auto=format&fit=crop",
             "Crisp, orange carrots perfect for cooking and salads.", 1),
            ("Cherry Tomatoes 250g", "Produce", 45.00, 100,
             "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=600&auto=format&fit=crop",
             "Sweet, bite-sized cherry tomatoes for fresh salads.", 1),
            ("Fresh Baby Spinach 200g", "Produce", 40.00, 80,
             "https://images.unsplash.com/photo-1576045057995-568f588f82fb?q=80&w=600&auto=format&fit=crop",
             "Tender baby spinach packed with iron and nutrients.", 1),
            ("Fresh Broccoli Crown", "Produce", 55.00, 110,
             "https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?q=80&w=600&auto=format&fit=crop",
             "Vibrant green broccoli crowns, perfect for steaming.", 1),

            # Verified Bakery
            ("Whole Wheat Bread", "Bakery", 45.00, 80,
             "https://images.unsplash.com/photo-1598373182133-52452f7691ef?q=80&w=600&auto=format&fit=crop",
             "Freshly baked whole wheat bread with natural grains.", 1),
            ("Butter Croissants (6-pack)", "Bakery", 140.00, 30,
             "https://images.unsplash.com/photo-1555507036-ab1f40ce88ca?q=80&w=600&auto=format&fit=crop",
             "Flaky, buttery French croissants baked fresh this morning.", 1),

            # Verified Pantry & Meat
            ("Natural Almond Butter 200g", "Pantry", 350.00, 50,
             "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?q=80&w=600&auto=format&fit=crop",
             "Smooth almond butter with no added sugar or preservatives.", 1),
            ("Whole Grain Pasta 500g", "Pantry", 110.00, 200,
             "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=600&auto=format&fit=crop",
             "Nutritious whole grain pasta packed with dietary fiber.", 1),
            ("Premium Olive Oil 500ml", "Pantry", 450.00, 40,
             "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?q=80&w=600&auto=format&fit=crop",
             "Extra virgin olive oil with fruity, aromatic notes.", 1),
            ("Long Grain Brown Rice 1kg", "Pantry", 95.00, 150,
             "https://images.unsplash.com/photo-1586201375761-83865001e31c?q=80&w=600&auto=format&fit=crop",
             "Nutty brown rice with a satisfying, chewy texture.", 1),
            ("Wholesome Granola Oats 400g", "Pantry", 160.00, 90,
             "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?q=80&w=600&auto=format&fit=crop",
             "Wholesome granola packed with seeds, nuts, and honey.", 1),
            ("Wild-Caught Salmon 500g", "Seafood", 550.00, 40,
             "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=600&auto=format&fit=crop",
             "Premium wild-caught salmon rich in omega-3 fatty acids.", 1)
        ]
        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()
    print("✅ Super Shopee Database initialized successfully!")


# This allows you to run `python database.py` in your terminal to instantly reset the DB for your demo
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Old database removed.")
    init_db()
    print("🎉 Fresh demo data generated!")import sqlite3
import os
from werkzeug.security import generate_password_hash

# Absolute Path Logic
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    # 1. Create tables
    curr.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    img_url TEXT,
                    description TEXT,
                    is_active INTEGER DEFAULT 1)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_username TEXT NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY(product_id) REFERENCES products(id))''')

    curr.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_username TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    order_date TEXT NOT NULL)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_at_purchase REAL NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id))''')

    # 2. Seed Users (Admin & Staff for your demo)
    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('staff', generate_password_hash('staff123'), 'Staff')
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    # 3. Seed Verified Supermarket Products
    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            # Verified Dairy
            ("Farm Fresh Whole Milk 1L", "Dairy", 68.00, 150, "https://images.unsplash.com/photo-1563636619-e9143da7973b?q=80&w=600&auto=format&fit=crop", "Locally sourced, creamy whole milk for your family.", 1),
            ("Premium Greek Yogurt 500g", "Dairy", 120.00, 100, "https://images.unsplash.com/photo-1574684039860-91a629b3bb88?q=80&w=600&auto=format&fit=crop", "Rich and thick Greek yogurt, packed with healthy probiotics.", 1),
            ("Aged Cheddar Cheese 200g", "Dairy", 220.00, 75, "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?q=80&w=600&auto=format&fit=crop", "Sharp aged cheddar with rich, complex flavor.", 1),
            ("Free-Range Eggs 1 Dozen", "Dairy", 85.00, 120, "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?q=80&w=600&auto=format&fit=crop", "Premium free-range eggs from happy, well-fed chickens.", 1),

            # Verified Produce (Fruits & Veggies)
            ("Organic Bananas 1 Dozen", "Produce", 60.00, 200, "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop", "Golden, ripe organic bananas rich in potassium.", 1),
            ("Honeycrisp Apples 1kg", "Produce", 180.00, 250, "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=600&auto=format&fit=crop", "Crisp, juicy apples bursting with natural flavor.", 1),
            ("Fresh Blueberries 250g", "Produce", 150.00, 60, "https://images.unsplash.com/photo-1498557850523-fc30739cb37b?q=80&w=600&auto=format&fit=crop", "Antioxidant-rich blueberries, perfect for smoothies.", 1),
            ("Ripe Avocados 2 Pack", "Produce", 120.00, 120, "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?q=80&w=600&auto=format&fit=crop", "Creamy Hass avocados ready for fresh guacamole.", 1),
            ("Fresh Carrots 1kg", "Produce", 50.00, 180, "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?q=80&w=600&auto=format&fit=crop", "Crisp, orange carrots perfect for cooking and salads.", 1),
            ("Cherry Tomatoes 250g", "Produce", 45.00, 100, "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=600&auto=format&fit=crop", "Sweet, bite-sized cherry tomatoes for fresh salads.", 1),
            ("Fresh Baby Spinach 200g", "Produce", 40.00, 80, "https://images.unsplash.com/photo-1576045057995-568f588f82fb?q=80&w=600&auto=format&fit=crop", "Tender baby spinach packed with iron and nutrients.", 1),
            ("Fresh Broccoli Crown", "Produce", 55.00, 110, "https://images.unsplash.com/photo-1584270354949-c26b0d5b4a0c?q=80&w=600&auto=format&fit=crop", "Vibrant green broccoli crowns, perfect for steaming.", 1),

            # Verified Bakery
            ("Whole Wheat Bread", "Bakery", 45.00, 80, "https://images.unsplash.com/photo-1598373182133-52452f7691ef?q=80&w=600&auto=format&fit=crop", "Freshly baked whole wheat bread with natural grains.", 1),
            ("Butter Croissants (6-pack)", "Bakery", 140.00, 30, "https://images.unsplash.com/photo-1555507036-ab1f40ce88ca?q=80&w=600&auto=format&fit=crop", "Flaky, buttery French croissants baked fresh this morning.", 1),

            # Verified Pantry & Meat
            ("Natural Almond Butter 200g", "Pantry", 350.00, 50, "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?q=80&w=600&auto=format&fit=crop", "Smooth almond butter with no added sugar or preservatives.", 1),
            ("Whole Grain Pasta 500g", "Pantry", 110.00, 200, "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=600&auto=format&fit=crop", "Nutritious whole grain pasta packed with dietary fiber.", 1),
            ("Premium Olive Oil 500ml", "Pantry", 450.00, 40, "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?q=80&w=600&auto=format&fit=crop", "Extra virgin olive oil with fruity, aromatic notes.", 1),
            ("Long Grain Brown Rice 1kg", "Pantry", 95.00, 150, "https://images.unsplash.com/photo-1586201375761-83865001e31c?q=80&w=600&auto=format&fit=crop", "Nutty brown rice with a satisfying, chewy texture.", 1),
            ("Wholesome Granola Oats 400g", "Pantry", 160.00, 90, "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?q=80&w=600&auto=format&fit=crop", "Wholesome granola packed with seeds, nuts, and honey.", 1),
            ("Wild-Caught Salmon 500g", "Seafood", 550.00, 40, "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=600&auto=format&fit=crop", "Premium wild-caught salmon rich in omega-3 fatty acids.", 1)
        ]
        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()
    print("✅ Super Shopee Database initialized successfully!")

# This allows you to run `python database.py` in your terminal to instantly reset the DB for your demo
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Old database removed.")
    init_db()
    print("🎉 Fresh demo data generated!")
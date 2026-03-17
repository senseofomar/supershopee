import sqlite3
import os
from werkzeug.security import generate_password_hash

# Absolute Path Logic
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    # Module 1: Authentication & User Management
    curr.execute('''CREATE TABLE IF NOT EXISTS users
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        username
                        TEXT
                        UNIQUE,
                        password
                        TEXT,
                        role
                        TEXT
                    )''')

    # Module 2: Product Catalog Management
    curr.execute('''CREATE TABLE IF NOT EXISTS products
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        name
                        TEXT,
                        category
                        TEXT,
                        price
                        REAL,
                        stock
                        INTEGER,
                        img_url
                        TEXT,
                        description
                        TEXT
                    )''')

    # Module 3: Order Management
    curr.execute('''CREATE TABLE IF NOT EXISTS orders
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        customer_username
                        TEXT,
                        total_amount
                        REAL,
                        status
                        TEXT,
                        order_date
                        TEXT
                    )''')

    # Module 4: Order Items Tracking
    curr.execute('''CREATE TABLE IF NOT EXISTS order_items
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        order_id
                        INTEGER,
                        product_id
                        INTEGER,
                        quantity
                        INTEGER,
                        price_at_purchase
                        REAL
                    )''')

    # Seed demo users for your presentation
    users = [('admin', generate_password_hash('admin123'), 'Admin'),
             ('cashier_sarah', generate_password_hash('cashier123'), 'Cashier')]
    curr.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?,?,?)", users)

    # Seed fresh grocery products if not exists
    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Organic Bananas (1 Dozen)", "Produce", 60.0, 150,
             "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=500&auto=format&fit=crop",
             "Fresh organic bananas, rich in potassium and natural sweetness."),
            ("Whole Milk (1L)", "Dairy", 68.0, 80,
             "https://images.unsplash.com/photo-1550583724-b2692b0b0d66?q=80&w=500&auto=format&fit=crop",
             "Fresh whole milk, perfect for your family breakfast."),
            ("Whole Wheat Bread", "Bakery", 45.0, 60,
             "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=500&auto=format&fit=crop",
             "Freshly baked whole wheat bread with natural grains."),
            ("Fresh Carrots (1kg)", "Produce", 50.0, 200,
             "https://images.unsplash.com/photo-1447518352343-13983f90e552?q=80&w=500&auto=format&fit=crop",
             "Crisp, colorful organic carrots perfect for cooking and snacking."),
            ("Greek Yogurt (500g)", "Dairy", 120.0, 100,
             "https://images.unsplash.com/photo-1488477181946-6428a0291840?q=80&w=500&auto=format&fit=crop",
             "Creamy, protein-rich Greek yogurt for a healthy lifestyle."),
            ("Almond Butter (250g)", "Pantry", 450.0, 50,
             "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=500&auto=format&fit=crop",
             "Smooth almond butter with no added sugar or preservatives."),
            ("Free-Range Eggs (Dozen)", "Dairy", 80.0, 120,
             "https://images.unsplash.com/photo-1578295272aca8206b6f1fb76f80f3d7a4e8f36?q=80&w=500&auto=format&fit=crop",
             "Premium free-range eggs from happy, well-fed chickens."),
            ("Cherry Tomatoes (250g)", "Produce", 40.0, 100,
             "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=500&auto=format&fit=crop",
             "Sweet, bite-sized cherry tomatoes for fresh salads."),
            ("Whole Grain Pasta (500g)", "Pantry", 150.0, 200,
             "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=500&auto=format&fit=crop",
             "Nutritious whole grain pasta packed with fiber."),
            ("Honeycrisp Apples (1kg)", "Produce", 180.0, 250,
             "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=500&auto=format&fit=crop",
             "Crisp, juicy apples bursting with natural flavor.")
        ]

        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description) VALUES (?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()
    print(f"✅ Super Shopee Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
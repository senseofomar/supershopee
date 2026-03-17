import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    # Create tables
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

    # Seed users (only if empty)
    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    # Seed products (only if empty)
    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Fresh Whole Milk 1L", "Dairy", 85.00, 150, "https://images.unsplash.com/photo-1550583724-b2692b0b0d66?q=80&w=600&auto=format&fit=crop", "Fresh, creamy whole milk for your family.", 1),
            ("Organic Bananas 1kg", "Fruits", 65.00, 200, "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop", "Golden, ripe organic bananas rich in potassium.", 1),
            ("Whole Wheat Bread", "Bakery", 55.00, 80, "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600&auto=format&fit=crop", "Freshly baked whole wheat bread with natural grains.", 1),
            ("Fresh Carrots 500g", "Vegetables", 45.00, 180, "https://images.unsplash.com/photo-1447518352343-13983f90e552?q=80&w=600&auto=format&fit=crop", "Crisp, orange carrots perfect for cooking and salads.", 1),
            ("Greek Yogurt 500g", "Dairy", 120.00, 100, "https://images.unsplash.com/photo-1488477181946-6428a0291840?q=80&w=600&auto=format&fit=crop", "Creamy, protein-rich Greek yogurt for a healthy lifestyle.", 1),
            ("Natural Almond Butter 200g", "Pantry", 220.00, 50, "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=600&auto=format&fit=crop", "Smooth almond butter with no added sugar or preservatives.", 1),
            ("Free-Range Eggs 1 Dozen", "Dairy", 150.00, 120, "https://images.unsplash.com/photo-1578295272aca8206b6f1fb76f80f3d7a4e8f36?q=80&w=600&auto=format&fit=crop", "Premium free-range eggs from happy, well-fed chickens.", 1),
            ("Cherry Tomatoes 250g", "Vegetables", 90.00, 100, "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=600&auto=format&fit=crop", "Sweet, bite-sized cherry tomatoes for fresh salads.", 1),
            ("Whole Grain Pasta 500g", "Pantry", 75.00, 200, "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=600&auto=format&fit=crop", "Nutritious whole grain pasta packed with fiber.", 1),
            ("Honeycrisp Apples 1kg", "Fruits", 110.00, 250, "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=600&auto=format&fit=crop", "Crisp, juicy apples bursting with natural flavor.", 1),
            ("Aged Cheddar Cheese 200g", "Dairy", 220.00, 75, "https://images.unsplash.com/photo-1555939594-58d7cb561537?q=80&w=600&auto=format&fit=crop", "Sharp aged cheddar with rich, complex flavor.", 1),
            ("Fresh Baby Spinach 200g", "Vegetables", 95.00, 80, "https://images.unsplash.com/photo-1511537190424-f06628ca66d5?q=80&w=600&auto=format&fit=crop", "Tender baby spinach packed with iron and nutrients.", 1),
            ("Wild-Caught Salmon 500g", "Seafood", 450.00, 40, "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop", "Premium wild-caught salmon rich in omega-3 fatty acids.", 1),
            ("Long Grain Brown Rice 1kg", "Pantry", 110.00, 150, "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600&auto=format&fit=crop", "Nutty brown rice with a satisfying, chewy texture.", 1),
            ("Fresh Blueberries 250g", "Fruits", 180.00, 60, "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=600&auto=format&fit=crop", "Antioxidant-rich blueberries, perfect for smoothies.", 1),
            ("Premium Olive Oil 500ml", "Pantry", 350.00, 40, "https://images.unsplash.com/photo-1502224311726-72d15d3c5c16?q=80&w=600&auto=format&fit=crop", "Extra virgin olive oil with fruity, aromatic notes.", 1),
            ("Fresh Croissants Pack", "Bakery", 140.00, 30, "https://images.unsplash.com/photo-1585854870192-e5cd83cf7b73?q=80&w=600&auto=format&fit=crop", "Buttery, flaky French croissants fresh from our oven.", 1),
            ("Ripe Avocados 2 pack", "Fruits", 80.00, 120, "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?q=80&w=600&auto=format&fit=crop", "Creamy avocados ready for guacamole and salads.", 1),
            ("Wholesome Granola 400g", "Pantry", 160.00, 90, "https://images.unsplash.com/photo-1585518895894-94ccb9e9b3b6?q=80&w=600&auto=format&fit=crop", "Wholesome granola packed with seeds and nuts.", 1),
            ("Fresh Broccoli Crown 500g", "Vegetables", 65.00, 110, "https://images.unsplash.com/photo-1564617278893-a0ff63e35e6c?q=80&w=600&auto=format&fit=crop", "Vibrant green broccoli crowns, perfect for steaming or roasting.", 1),
        ]
        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
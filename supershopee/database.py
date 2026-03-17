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
                    username TEXT UNIQUE, 
                    password TEXT, 
                    role TEXT)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS products(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    category TEXT, 
                    price REAL, 
                    stock INTEGER,
                    img_url TEXT, 
                    description TEXT)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_username TEXT, 
                    total_amount REAL, 
                    status TEXT, 
                    order_date TEXT)''')

    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    order_id INTEGER, 
                    product_id INTEGER, 
                    quantity INTEGER, 
                    price_at_purchase REAL)''')

    # Seed users (ONLY if table is empty)
    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('cashier_sarah', generate_password_hash('cashier123'), 'Cashier'),
            ('staff_john', generate_password_hash('staff123'), 'Staff'),
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    # Seed products (ONLY if table is empty)
    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Organic Bananas", "Produce", 2.49, 150, "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop", "Fresh organic bananas, rich in potassium and natural sweetness."),
            ("Whole Milk 1L", "Dairy", 3.99, 80, "https://images.unsplash.com/photo-1550583724-b2692b0b0d66?q=80&w=600&auto=format&fit=crop", "Fresh whole milk, perfect for your family breakfast."),
            ("Whole Wheat Bread", "Bakery", 4.49, 60, "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600&auto=format&fit=crop", "Freshly baked whole wheat bread with natural grains."),
            ("Organic Carrots 2lb", "Produce", 2.99, 200, "https://images.unsplash.com/photo-1447518352343-13983f90e552?q=80&w=600&auto=format&fit=crop", "Crisp, colorful organic carrots perfect for cooking and snacking."),
            ("Greek Yogurt 500g", "Dairy", 5.49, 100, "https://images.unsplash.com/photo-1488477181946-6428a0291840?q=80&w=600&auto=format&fit=crop", "Creamy, protein-rich Greek yogurt for a healthy lifestyle."),
            ("Natural Almond Butter", "Pantry", 7.99, 50, "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=600&auto=format&fit=crop", "Smooth almond butter with no added sugar or preservatives."),
            ("Free-Range Eggs (Dozen)", "Dairy", 6.99, 120, "https://images.unsplash.com/photo-1578295272aca8206b6f1fb76f80f3d7a4e8f36?q=80&w=600&auto=format&fit=crop", "Premium free-range eggs from happy, well-fed chickens."),
            ("Cherry Tomatoes", "Produce", 3.99, 100, "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=600&auto=format&fit=crop", "Sweet, bite-sized cherry tomatoes for fresh salads."),
            ("Whole Grain Pasta 500g", "Pantry", 2.79, 200, "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=600&auto=format&fit=crop", "Nutritious whole grain pasta packed with fiber."),
            ("Honeycrisp Apples", "Produce", 1.49, 250, "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=600&auto=format&fit=crop", "Crisp, juicy apples bursting with natural flavor."),
            ("Aged Cheddar Cheese", "Dairy", 7.49, 75, "https://images.unsplash.com/photo-1555939594-58d7cb561537?q=80&w=600&auto=format&fit=crop", "Sharp aged cheddar with rich, complex flavor."),
            ("Fresh Baby Spinach 200g", "Produce", 3.49, 80, "https://images.unsplash.com/photo-1511537190424-f06628ca66d5?q=80&w=600&auto=format&fit=crop", "Tender baby spinach packed with iron and nutrients."),
            ("Wild-Caught Salmon Fillet", "Seafood", 12.99, 40, "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop", "Premium wild-caught salmon rich in omega-3 fatty acids."),
            ("Long Grain Brown Rice 2lb", "Pantry", 3.99, 150, "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600&auto=format&fit=crop", "Nutty brown rice with a satisfying, chewy texture."),
            ("Fresh Blueberries", "Produce", 5.99, 60, "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=600&auto=format&fit=crop", "Antioxidant-rich blueberries, perfect for smoothies."),
            ("Premium Olive Oil 500ml", "Pantry", 11.99, 40, "https://images.unsplash.com/photo-1502224311726-72d15d3c5c16?q=80&w=600&auto=format&fit=crop", "Extra virgin olive oil with fruity, aromatic notes."),
            ("Fresh Croissants (6-pack)", "Bakery", 5.99, 30, "https://images.unsplash.com/photo-1585854870192-e5cd83cf7b73?q=80&w=600&auto=format&fit=crop", "Buttery, flaky French croissants fresh from our oven."),
            ("Ripe Avocados", "Produce", 2.49, 120, "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?q=80&w=600&auto=format&fit=crop", "Creamy avocados ready for guacamole and salads."),
            ("Wholesome Granola Cereal", "Pantry", 5.49, 90, "https://images.unsplash.com/photo-1585518895894-94ccb9e9b3b6?q=80&w=600&auto=format&fit=crop", "Wholesome granola packed with seeds and nuts."),
            ("Fresh Broccoli Crowns", "Produce", 2.99, 110, "https://images.unsplash.com/photo-1564617278893-a0ff63e35e6c?q=80&w=600&auto=format&fit=crop", "Vibrant green broccoli crowns, perfect for steaming or roasting."),
        ]
        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description) VALUES (?, ?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully")
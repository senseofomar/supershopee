import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    curr.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL, stock INTEGER NOT NULL, img_url TEXT, description TEXT, is_active INTEGER DEFAULT 1)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, FOREIGN KEY(product_id) REFERENCES products(id))''')
    curr.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, total_amount REAL NOT NULL, status TEXT NOT NULL, order_date TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, price_at_purchase REAL NOT NULL, FOREIGN KEY(order_id) REFERENCES orders(id))''')

    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('cashier', generate_password_hash('cashier123'), 'Admin'),
            ('shopper', generate_password_hash('shopper123'), 'Customer'),
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        # EXACT LOCAL FILENAMES
        products = [
            # DAIRY
            ("Farm Fresh Milk 1L", "Dairy", 68.0, 150, "milk.jpg", "Locally sourced, creamy whole milk.", 1),
            ("Cheddar Cheese Block", "Dairy", 220.0, 75, "cheddar.jpg", "Sharp aged cheddar with rich flavor.", 1),
            ("Salted Butter 200g", "Dairy", 55.0, 90, "butter.jpg", "Creamy salted butter perfect for cooking.", 1),
            ("Greek Yogurt 500g", "Dairy", 120.0, 60, "yogurt.jpg", "Rich, thick, and probiotic-rich Greek yogurt.", 1),
            ("Mozzarella Cheese", "Dairy", 120.0, 45, "mozzarella.jpg", "Creamy mozzarella for pizza and pasta.", 1),

            # FRUITS
            ("Organic Bananas 1kg", "Fruits", 60.0, 200, "bananas.jpg", "Golden, ripe organic bananas.", 1),
            ("Fuji Apples 1kg", "Fruits", 180.0, 250, "apples.jpg", "Crisp, juicy red apples.", 1),
            ("Fresh Oranges 1kg", "Fruits", 110.0, 150, "oranges.jpg", "Sweet and tangy citrus oranges.", 1),
            ("Fresh Strawberries", "Fruits", 150.0, 60, "strawberries.jpg", "Bright red, sweet strawberries.", 1),
            ("Mango Alphonso", "Fruits", 200.0, 80, "mango.jpg", "Premium sweet mangoes from India.", 1),
            ("Fresh Watermelon", "Fruits", 90.0, 100, "watermelon.jpg", "Refreshing, hydrating whole watermelon.", 1),

            # VEGETABLES
            ("Fresh Potatoes 1kg", "Vegetables", 30.0, 300, "potatoes.jpg", "Farm-fresh cooking potatoes.", 1),
            ("Red Onions 1kg", "Vegetables", 40.0, 250, "onions.jpg", "Crisp red onions for everyday cooking.", 1),
            ("Fresh Red Tomatoes", "Vegetables", 45.0, 200, "tomatoes.jpg", "Juicy, ripe red tomatoes.", 1),
            ("Fresh Carrots 1kg", "Vegetables", 50.0, 180, "carrots.jpg", "Crunchy orange carrots packed with beta-carotene.", 1),
            ("Broccoli Crown 500g", "Vegetables", 55.0, 110, "broccoli.jpg", "Vibrant green broccoli.", 1),
            ("Spinach Fresh Bundle", "Vegetables", 35.0, 120, "spinach.jpg", "Fresh organic spinach leaves.", 1),
            ("Green Bell Peppers", "Vegetables", 45.0, 90, "peppers.jpg", "Crunchy and fresh green bell peppers.", 1),

            # BAKERY
            ("Whole Wheat Bread", "Bakery", 45.0, 80, "bread.jpg", "Freshly baked whole wheat loaf.", 1),
            ("Butter Croissants Pack", "Bakery", 140.0, 30, "croissants.jpg", "Flaky, buttery French croissants.", 1),
            ("Choco Chip Cookies", "Bakery", 90.0, 50, "cookies.jpg", "Freshly baked cookies with chocolate chunks.", 1),
            ("Blueberry Muffins", "Bakery", 110.0, 40, "muffins.jpg", "Soft muffins loaded with fresh blueberries.", 1),

            # PANTRY
            ("Basmati Rice 1kg", "Pantry", 120.0, 150, "rice.jpg", "Premium long-grain Basmati rice.", 1),
            ("Whole Grain Pasta", "Pantry", 110.0, 200, "pasta.jpg", "Nutritious whole grain pasta.", 1),
            ("Raw Almonds 500g", "Pantry", 480.0, 50, "almonds.jpg", "Crunchy, premium California almonds.", 1),
            ("Organic Honey 250g", "Pantry", 250.0, 60, "honey.jpg", "100% pure, natural raw honey.", 1),
            ("Sunflower Oil 1L", "Pantry", 120.0, 100, "oil.jpg", "Pure refined cooking oil.", 1),
            ("White Sugar 1kg", "Pantry", 40.0, 200, "sugar.jpg", "Fine white sugar crystals.", 1)
        ]

        curr.executemany("INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print("✅ Database initialized with manual local images!")
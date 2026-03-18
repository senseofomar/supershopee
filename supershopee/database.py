import sqlite3
import os
from werkzeug.security import generate_password_hash
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_placeholder(text):
    # Generates a sleek green image with the product name written on it
    encoded_text = urllib.parse.quote(text)
    return f"https://placehold.co/600x400/064e3b/ffffff?text={encoded_text}"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    curr.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,price REAL NOT NULL,stock INTEGER NOT NULL,img_url TEXT,description TEXT,is_active INTEGER DEFAULT 1)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items (id INTEGER PRIMARY KEY AUTOINCREMENT,customer_username TEXT NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL,FOREIGN KEY(product_id) REFERENCES products (id))''')
    curr.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, total_amount REAL NOT NULL, status TEXT NOT NULL, order_date TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, price_at_purchase REAL NOT NULL, FOREIGN KEY(order_id) REFERENCES orders(id))''')

    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [('admin', generate_password_hash('admin123'), 'Admin')]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            ("Farm Fresh Milk 1L", "Dairy", 68.00, 150, get_placeholder("Farm Fresh\nMilk 1L"), "Locally sourced, creamy whole milk.", 1),
            ("Greek Yogurt 500g", "Dairy", 120.00, 100, get_placeholder("Greek Yogurt\n500g"), "Rich, thick, and probiotic-rich.", 1),
            ("Cheddar Cheese", "Dairy", 220.00, 75, get_placeholder("Cheddar\nCheese Block"), "Sharp aged cheddar with rich flavor.", 1),
            ("Fresh Paneer 250g", "Dairy", 85.00, 60, get_placeholder("Fresh Paneer\n250g"), "Soft and fresh cottage cheese.", 1),
            ("Salted Butter 200g", "Dairy", 55.00, 90, get_placeholder("Salted Butter\n200g"), "Creamy salted butter.", 1),

            ("Organic Bananas", "Fruits", 60.00, 200, get_placeholder("Organic\nBananas"), "Golden, ripe organic bananas.", 1),
            ("Fuji Apples 1kg", "Fruits", 180.00, 250, get_placeholder("Fuji Apples\n1kg"), "Crisp, juicy red apples.", 1),
            ("Fresh Oranges", "Fruits", 110.00, 150, get_placeholder("Fresh Oranges\n1kg"), "Sweet and tangy citrus oranges.", 1),
            ("Strawberries", "Fruits", 150.00, 60, get_placeholder("Fresh\nStrawberries"), "Bright red, sweet strawberries.", 1),
            ("Green Grapes", "Fruits", 90.00, 100, get_placeholder("Green Grapes\n500g"), "Seedless, crunchy green grapes.", 1),

            ("Fresh Potatoes", "Vegetables", 30.00, 300, get_placeholder("Fresh Potatoes\n1kg"), "Farm-fresh cooking potatoes.", 1),
            ("Red Onions 1kg", "Vegetables", 40.00, 250, get_placeholder("Red Onions\n1kg"), "Crisp red onions for everyday cooking.", 1),
            ("Red Tomatoes", "Vegetables", 45.00, 200, get_placeholder("Red Tomatoes\n1kg"), "Juicy, ripe red tomatoes.", 1),
            ("Fresh Carrots", "Vegetables", 50.00, 180, get_placeholder("Fresh Carrots\n1kg"), "Crunchy orange carrots.", 1),
            ("Broccoli Crown", "Vegetables", 55.00, 110, get_placeholder("Broccoli\nCrown"), "Vibrant green broccoli.", 1),

            ("Whole Wheat Bread", "Bakery", 45.00, 80, get_placeholder("Whole Wheat\nBread"), "Freshly baked whole wheat loaf.", 1),
            ("Butter Croissants", "Bakery", 140.00, 30, get_placeholder("Butter\nCroissants"), "Flaky, buttery French croissants.", 1),
            ("Choc-Chip Cookies", "Bakery", 90.00, 50, get_placeholder("Choc-Chip\nCookies"), "Freshly baked cookies.", 1),

            ("Basmati Rice 1kg", "Pantry", 120.00, 150, get_placeholder("Basmati Rice\n1kg"), "Premium long-grain Basmati rice.", 1),
            ("Whole Grain Pasta", "Pantry", 110.00, 200, get_placeholder("Whole Grain\nPasta"), "Nutritious whole grain pasta.", 1),
            ("Virgin Olive Oil", "Pantry", 450.00, 40, get_placeholder("Virgin Olive\nOil 500ml"), "Cold-pressed extra virgin olive oil.", 1),
            ("Raw Almonds 500g", "Pantry", 480.00, 50, get_placeholder("Raw Almonds\n500g"), "Crunchy, premium California almonds.", 1),
            ("Organic Honey", "Pantry", 250.00, 60, get_placeholder("Organic Honey\n250g"), "100% pure, natural raw honey.", 1),

            ("Roasted Coffee", "Beverages", 350.00, 45, get_placeholder("Roasted Coffee\nBeans"), "Aromatic, dark roasted coffee beans.", 1),
            ("Green Tea Leaves", "Beverages", 180.00, 70, get_placeholder("Green Tea\nLeaves"), "Antioxidant-rich loose green tea.", 1)
        ]
        curr.executemany("INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print("✅ Dummy images replaced with reliable Text-Blocks!")
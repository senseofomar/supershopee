import sqlite3
import os
from werkzeug.security import generate_password_hash
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

    curr.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,price REAL NOT
                                                        NULL,stock INTEGER NOT NULL,img_url TEXT,description TEXT,is_active INTEGER DEFAULT 1)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items (id INTEGER PRIMARY KEY AUTOINCREMENT,customer_username TEXT NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL,FOREIGN KEY(product_id) REFERENCES products (id))''')
    curr.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, total_amount REAL NOT NULL, status TEXT NOT NULL, order_date TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER NOT NULL,product_name TEXT NOT NULL,quantity INTEGER NOT NULL,price_at_purchase REAL NOT NULL,FOREIGN KEY(order_id) REFERENCES orders (id))''')

    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('cashier', generate_password_hash('cashier123'), 'Admin'),
            ('shopper', generate_password_hash('shopper123'), 'Customer'),
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            # DAIRY - REAL UNSPLASH IMAGES
            ("Farm Fresh Milk 1L", "Dairy", 68.00, 150, "https://images.unsplash.com/photo-1550583902-d158ca0aa46b?w=600&h=400&fit=crop", "Locally sourced, creamy whole milk.", 1),
            ("Greek Yogurt 500g", "Dairy", 120.00, 100, "https://images.unsplash.com/photo-1488477181946-6428a0291840?w=600&h=400&fit=crop", "Rich, thick, and probiotic-rich.", 1),
            ("Cheddar Cheese", "Dairy", 220.00, 75, "https://images.unsplash.com/photo-1628840042765-356cda07f4ee?w=600&h=400&fit=crop", "Sharp aged cheddar with rich flavor.", 1),
            ("Fresh Paneer 250g", "Dairy", 85.00, 60, "https://images.unsplash.com/photo-1599599810694-b5ac4dd64b59?w=600&h=400&fit=crop", "Soft and fresh cottage cheese.", 1),
            ("Salted Butter 200g", "Dairy", 55.00, 90, "https://images.unsplash.com/photo-1589985643636-891e7e12e88e?w=600&h=400&fit=crop", "Creamy salted butter.", 1),

            # FRUITS - REAL UNSPLASH IMAGES
            ("Organic Bananas", "Fruits", 60.00, 200, "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop", "Golden, ripe organic bananas.", 1),
            ("Fuji Apples 1kg", "Fruits", 180.00, 250, "https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=600&h=400&fit=crop", "Crisp, juicy red apples.", 1),
            ("Fresh Oranges", "Fruits", 110.00, 150, "https://images.unsplash.com/photo-1584202411487-58d12f61ae1e?w=600&h=400&fit=crop", "Sweet and tangy citrus oranges.", 1),
            ("Strawberries", "Fruits", 150.00, 60, "https://images.unsplash.com/photo-1587805692736-604643985180?w=600&h=400&fit=crop", "Bright red, sweet strawberries.", 1),
            ("Green Grapes", "Fruits", 90.00, 100, "https://images.unsplash.com/photo-1537642220052-8b697a814b4f?w=600&h=400&fit=crop", "Seedless, crunchy green grapes.", 1),

            # VEGETABLES - REAL UNSPLASH IMAGES
            ("Fresh Potatoes", "Vegetables", 30.00, 300, "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&h=400&fit=crop", "Farm-fresh cooking potatoes.", 1),
            ("Red Onions 1kg", "Vegetables", 40.00, 250, "https://images.unsplash.com/photo-1594689832679-8f4da9cf08d9?w=600&h=400&fit=crop", "Crisp red onions for everyday cooking.", 1),
            ("Red Tomatoes", "Vegetables", 45.00, 200, "https://images.unsplash.com/photo-1566781016486-d03a1b94d34c?w=600&h=400&fit=crop", "Juicy, ripe red tomatoes.", 1),
            ("Fresh Carrots", "Vegetables", 50.00, 180, "https://images.unsplash.com/photo-1461080359090-2049af367a67?w=600&h=400&fit=crop", "Crunchy orange carrots.", 1),
            ("Broccoli Crown", "Vegetables", 55.00, 110, "https://images.unsplash.com/photo-1537693410547-3b0fbf74cdeb?w=600&h=400&fit=crop", "Vibrant green broccoli.", 1),

            # BAKERY - REAL UNSPLASH IMAGES
            ("Whole Wheat Bread", "Bakery", 45.00, 80, "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600&h=400&fit=crop", "Freshly baked whole wheat loaf.", 1),
            ("Butter Croissants", "Bakery", 140.00, 30, "https://images.unsplash.com/photo-1590969519798-7b5f55a21f44?w=600&h=400&fit=crop", "Flaky, buttery French croissants.", 1),
            ("Choc-Chip Cookies", "Bakery", 90.00, 50, "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600&h=400&fit=crop", "Freshly baked cookies.", 1),

            # PANTRY - REAL UNSPLASH IMAGES
            ("Basmati Rice 1kg", "Pantry", 120.00, 150, "https://images.unsplash.com/photo-1596552183021-b47df9f0c014?w=600&h=400&fit=crop", "Premium long-grain Basmati rice.", 1),
            ("Whole Grain Pasta", "Pantry", 110.00, 200, "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop", "Nutritious whole grain pasta.", 1),
            ("Virgin Olive Oil", "Pantry", 450.00, 40, "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&h=400&fit=crop", "Cold-pressed extra virgin olive oil.", 1),
            ("Raw Almonds 500g", "Pantry", 480.00, 50, "https://images.unsplash.com/photo-1585707862349-85d69d3b9e78?w=600&h=400&fit=crop", "Crunchy, premium California almonds.", 1),
            ("Organic Honey", "Pantry", 250.00, 60, "https://images.unsplash.com/photo-1584008148986-b14a2a9b0ae8?w=600&h=400&fit=crop", "100% pure, natural raw honey.", 1),

            # BEVERAGES - REAL UNSPLASH IMAGES
            ("Roasted Coffee", "Beverages", 350.00, 45, "https://images.unsplash.com/photo-1497935586351-b67a49e29331?w=600&h=400&fit=crop", "Aromatic, dark roasted coffee beans.", 1),
            ("Green Tea Leaves", "Beverages", 180.00, 70, "https://images.unsplash.com/photo-1597318619738-813dfa27aa47?w=600&h=400&fit=crop", "Antioxidant-rich loose green tea.", 1),
        ]
        curr.executemany("INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print("✅ Database initialized with real product images from Unsplash!")
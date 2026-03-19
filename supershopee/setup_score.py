import os
import sqlite3
import urllib.request
import time
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# 28 Reliable URLs
PRODUCTS_DATA = [
    # DAIRY
    ("milk.jpg", "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&q=80", "Farm Fresh Milk 1L", "Dairy", 68.0, 150, "Locally sourced, creamy whole milk."),
    ("cheese.jpg", "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=600&q=80", "Cheddar Cheese Block", "Dairy", 220.0, 75, "Sharp aged cheddar with rich flavor."),
    ("butter.jpg", "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=600&q=80", "Salted Butter 200g", "Dairy", 55.0, 90, "Creamy salted butter perfect for cooking."),
    ("yogurt.jpg", "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&q=80", "Greek Yogurt 500g", "Dairy", 120.0, 60, "Rich, thick, and probiotic-rich Greek yogurt."),
    ("mozzarella.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Mozzarella_di_bufala_campana_2.jpg/600px-Mozzarella_di_bufala_campana_2.jpg", "Mozzarella Cheese", "Dairy", 120.0, 45, "Creamy mozzarella for pizza and pasta."),

    # FRUITS
    ("bananas.jpg", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80", "Organic Bananas 1kg", "Fruits", 60.0, 200, "Golden, ripe organic bananas."),
    ("apples.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/600px-Red_Apple.jpg", "Fuji Apples 1kg", "Fruits", 180.0, 250, "Crisp, juicy red apples."),
    ("oranges.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Orange-Fruit-Pieces.jpg/600px-Orange-Fruit-Pieces.jpg", "Fresh Oranges 1kg", "Fruits", 110.0, 150, "Sweet and tangy citrus oranges."),
    ("strawberries.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/PerfectStrawberry.jpg/600px-PerfectStrawberry.jpg", "Fresh Strawberries", "Fruits", 150.0, 60, "Bright red, sweet strawberries."),
    ("mango.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Hapus_Mango.jpg/600px-Hapus_Mango.jpg", "Mango Alphonso", "Fruits", 200.0, 80, "Premium sweet mangoes from India."),
    ("watermelon.jpg", "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600&q=80", "Fresh Watermelon", "Fruits", 90.0, 100, "Refreshing, hydrating whole watermelon."),

    # VEGETABLES
    ("potatoes.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Patates.jpg/600px-Patates.jpg", "Fresh Potatoes 1kg", "Vegetables", 30.0, 300, "Farm-fresh cooking potatoes."),
    ("onions.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Onion_on_White.JPG/600px-Onion_on_White.JPG", "Red Onions 1kg", "Vegetables", 40.0, 250, "Crisp red onions for everyday cooking."),
    ("tomatoes.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Tomato_je.jpg/600px-Tomato_je.jpg", "Fresh Red Tomatoes", "Vegetables", 45.0, 200, "Juicy, ripe red tomatoes."),
    ("carrots.jpg", "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&q=80", "Fresh Carrots 1kg", "Vegetables", 50.0, 180, "Crunchy orange carrots packed with beta-carotene."),
    ("broccoli.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Broccoli_and_cross_section_edit.jpg/600px-Broccoli_and_cross_section_edit.jpg", "Broccoli Crown 500g", "Vegetables", 55.0, 110, "Vibrant green broccoli."),
    ("spinach.jpg", "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&q=80", "Spinach Fresh Bundle", "Vegetables", 35.0, 120, "Fresh organic spinach leaves."),
    ("peppers.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Green_bell_pepper.jpg/600px-Green_bell_pepper.jpg", "Green Bell Peppers", "Vegetables", 45.0, 90, "Crunchy and fresh green bell peppers."),

    # BAKERY
    ("bread.jpg", "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&q=80", "Whole Wheat Bread", "Bakery", 45.0, 80, "Freshly baked whole wheat loaf."),
    ("croissants.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Croissant_parts.jpg/600px-Croissant_parts.jpg", "Butter Croissants Pack", "Bakery", 140.0, 30, "Flaky, buttery French croissants."),
    ("cookies.jpg", "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600&q=80", "Choco Chip Cookies", "Bakery", 90.0, 50, "Freshly baked cookies with chocolate chunks."),
    ("muffins.jpg", "https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=600&q=80", "Blueberry Muffins", "Bakery", 110.0, 40, "Soft muffins loaded with fresh blueberries."),

    # PANTRY
    ("rice.jpg", "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80", "Basmati Rice 1kg", "Pantry", 120.0, 150, "Premium long-grain Basmati rice."),
    ("pasta.jpg", "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&q=80", "Whole Grain Pasta", "Pantry", 110.0, 200, "Nutritious whole grain pasta."),
    ("almonds.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Almonds_1.jpg/600px-Almonds_1.jpg", "Raw Almonds 500g", "Pantry", 480.0, 50, "Crunchy, premium California almonds."),
    ("honey.jpg", "https://images.unsplash.com/photo-1584286595398-a59f21d313f5?w=600&q=80", "Organic Honey 250g", "Pantry", 250.0, 60, "100% pure, natural raw honey."),
    ("oil.jpg", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&q=80", "Sunflower Oil 1L", "Pantry", 120.0, 100, "Pure refined cooking oil."),
    ("sugar.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Sucre_blanc.jpg/600px-Sucre_blanc.jpg", "White Sugar 1kg", "Pantry", 40.0, 200, "Fine white sugar crystals.")
]

def download_images():
    print("⏳ Downloading 28 high-quality images. Waiting 2 seconds between each to bypass bot-blockers...")
    for i, (filename, url, _, _, _, _, _) in enumerate(PRODUCTS_DATA, 1):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            try:
                # Disguise request to prevent 403 Forbidden errors
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"  [{i}/28] ✓ Downloaded {filename}")
                time.sleep(2) # CRITICAL: This bypasses the 429 Too Many Requests error!
            except Exception as e:
                print(f"  [{i}/28] ❌ Failed to download {filename}: {e}")
        else:
            print(f"  [{i}/28] ⚡ {filename} already exists, skipping.")

def setup_database():
    print("\n⏳ Rebuilding your database to use the local files...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()

    curr.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL, stock INTEGER NOT NULL, img_url TEXT, description TEXT, is_active INTEGER DEFAULT 1)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS cart_items (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, FOREIGN KEY(product_id) REFERENCES products(id))''')
    curr.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_username TEXT NOT NULL, total_amount REAL NOT NULL, status TEXT NOT NULL, order_date TEXT NOT NULL)''')
    curr.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_name TEXT NOT NULL, quantity INTEGER NOT NULL, price_at_purchase REAL NOT NULL, FOREIGN KEY(order_id) REFERENCES orders(id))''')

    users = [
        ('admin', generate_password_hash('admin123'), 'Admin'),
        ('cashier', generate_password_hash('cashier123'), 'Admin'),
        ('shopper', generate_password_hash('shopper123'), 'Customer'),
    ]
    curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    db_products = []
    for filename, _, name, category, price, stock, description in PRODUCTS_DATA:
        db_products.append((name, category, price, stock, filename, description, 1))

    curr.executemany("INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)", db_products)

    conn.commit()
    conn.close()
    print("  ✓ Database rebuilt successfully!")

if __name__ == "__main__":
    download_images()
    setup_database()
    print("\n🎉 ALL DONE! Start your app with `python app.py` and enjoy your flawless local store.")
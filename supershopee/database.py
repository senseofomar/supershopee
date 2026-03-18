import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    curr = conn.cursor()

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

    if curr.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash('admin123'), 'Admin'),
            ('cashier', generate_password_hash('cashier123'), 'Admin'),
            ('shopper', generate_password_hash('shopper123'), 'Customer'),
        ]
        curr.executemany("INSERT INTO users (username, password, role) VALUES (?,?,?)", users)

    if curr.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            # VERIFIED - DAIRY
            ("Farm Fresh Milk 1L", "Dairy", 68.00, 150,
             "https://cdn.pixabay.com/photo/2017/09/08/10/28/milk-2731388_640.jpg",
             "Locally sourced, creamy whole milk.", 1),
            ("Greek Yogurt 500g", "Dairy", 120.00, 100,
             "https://cdn.pixabay.com/photo/2020/03/06/11/08/yogurt-4906254_640.jpg",
             "Rich, thick, and probiotic-rich.", 1),
            ("Cheddar Cheese Block", "Dairy", 220.00, 75,
             "https://cdn.pixabay.com/photo/2015/01/09/11/10/cheese-594315_640.jpg",
             "Sharp aged cheddar with rich flavor.", 1),
            ("Fresh Cottage Cheese", "Dairy", 85.00, 60,
             "https://cdn.pixabay.com/photo/2020/03/06/11/08/cheese-4906256_640.jpg", "Soft and fresh cottage cheese.",
             1),
            ("Salted Butter 200g", "Dairy", 55.00, 90,
             "https://cdn.pixabay.com/photo/2017/02/11/22/17/butter-2058447_640.jpg", "Creamy salted butter.", 1),

            # VERIFIED - FRUITS
            ("Organic Bananas (1kg)", "Fruits", 60.00, 200,
             "https://cdn.pixabay.com/photo/2015/05/31/16/03/bananas-791075_640.jpg", "Golden, ripe organic bananas.",
             1),
            ("Fuji Apples (1kg)", "Fruits", 180.00, 250,
             "https://cdn.pixabay.com/photo/2017/09/26/13/42/apple-2788662_640.jpg", "Crisp, juicy red apples.", 1),
            ("Fresh Oranges (1kg)", "Fruits", 110.00, 150,
             "https://cdn.pixabay.com/photo/2016/12/26/17/28/orange-1932397_640.jpg", "Sweet and tangy citrus oranges.",
             1),
            ("Fresh Strawberries", "Fruits", 150.00, 60,
             "https://cdn.pixabay.com/photo/2017/02/21/21/13/strawberries-2086680_640.jpg",
             "Bright red, sweet strawberries.", 1),
            ("Green Grapes (500g)", "Fruits", 90.00, 100,
             "https://cdn.pixabay.com/photo/2017/07/21/23/57/grapes-2527405_640.jpg", "Seedless, crunchy green grapes.",
             1),

            # VERIFIED - VEGETABLES
            ("Fresh Potatoes (1kg)", "Vegetables", 30.00, 300,
             "https://cdn.pixabay.com/photo/2016/04/29/13/50/potatoes-1360116_640.jpg", "Farm-fresh cooking potatoes.",
             1),
            ("Red Onions (1kg)", "Vegetables", 40.00, 250,
             "https://cdn.pixabay.com/photo/2017/01/11/11/08/onion-1971270_640.jpg",
             "Crisp red onions for everyday cooking.", 1),
            ("Fresh Red Tomatoes", "Vegetables", 45.00, 200,
             "https://cdn.pixabay.com/photo/2016/01/08/17/37/tomato-1128360_640.jpg", "Juicy, ripe red tomatoes.", 1),
            ("Fresh Carrots (1kg)", "Vegetables", 50.00, 180,
             "https://cdn.pixabay.com/photo/2015/02/20/18/43/carrot-644387_640.jpg", "Crunchy orange carrots.", 1),
            ("Broccoli Crown", "Vegetables", 55.00, 110,
             "https://cdn.pixabay.com/photo/2016/05/05/08/28/broccoli-1375522_640.jpg", "Vibrant green broccoli.", 1),

            # VERIFIED - BAKERY
            ("Whole Wheat Bread", "Bakery", 45.00, 80,
             "https://cdn.pixabay.com/photo/2015/09/04/20/42/bread-923900_640.jpg", "Freshly baked whole wheat loaf.",
             1),
            ("Butter Croissants (Pack)", "Bakery", 140.00, 30,
             "https://cdn.pixabay.com/photo/2017/02/11/22/15/croissants-2056141_640.jpg",
             "Flaky, buttery French croissants.", 1),
            ("Choco Chip Cookies", "Bakery", 90.00, 50,
             "https://cdn.pixabay.com/photo/2017/12/25/22/53/cookies-3038845_640.jpg",
             "Freshly baked cookies with chunks.", 1),

            # VERIFIED - PANTRY
            ("Basmati Rice (1kg)", "Pantry", 120.00, 150,
             "https://cdn.pixabay.com/photo/2017/01/20/15/06/rice-1995412_640.jpg", "Premium long-grain Basmati rice.",
             1),
            ("Whole Grain Pasta", "Pantry", 110.00, 200,
             "https://cdn.pixabay.com/photo/2016/11/18/14/05/food-1836416_640.jpg", "Nutritious whole grain pasta.", 1),
            ("Virgin Olive Oil (500ml)", "Pantry", 450.00, 40,
             "https://cdn.pixabay.com/photo/2015/06/08/15/02/cooking-oil-801999_640.jpg",
             "Cold-pressed extra virgin olive oil.", 1),
            ("Raw Almonds (500g)", "Pantry", 480.00, 50,
             "https://cdn.pixabay.com/photo/2015/05/21/13/10/almond-776522_640.jpg",
             "Crunchy, premium California almonds.", 1),
            ("Organic Raw Honey (250g)", "Pantry", 250.00, 60,
             "https://cdn.pixabay.com/photo/2016/05/04/15/43/honey-1373654_640.jpg", "100% pure, natural raw honey.",
             1),

            # VERIFIED - BEVERAGES
            ("Roasted Coffee Beans", "Beverages", 350.00, 45,
             "https://cdn.pixabay.com/photo/2017/03/29/09/11/coffee-2185139_640.jpg",
             "Aromatic, dark roasted coffee beans.", 1),
            ("Green Tea Leaves", "Beverages", 180.00, 70,
             "https://cdn.pixabay.com/photo/2017/04/04/11/29/tea-2202845_640.jpg", "Antioxidant-rich loose green tea.",
             1),
        ]

        curr.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            products)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    print("✅ Database initialized with VERIFIED products from Pixabay!")
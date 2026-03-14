from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supershopeesecretkey"

# Configuration for Image Uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Create tables
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users
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
                )
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS products
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
                )
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS orders
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
                )
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS order_items
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
                )
                """)

    # Seed admin user if not exists
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'Admin')
        )

    # Seed products if not exists
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products_data = [
            ("Organic Bananas", "Produce", 2.49, 150,
             "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=500&auto=format&fit=crop",
             "Fresh organic bananas, great source of potassium"),
            ("Whole Milk", "Dairy", 3.99, 80,
             "https://images.unsplash.com/photo-1563056169-6d532e13e7b1?q=80&w=500&auto=format&fit=crop",
             "Fresh whole milk, 1 gallon"),
            ("Fresh Bread", "Bakery", 2.99, 60,
             "https://images.unsplash.com/photo-1549931295-c90dc2a2b1df?q=80&w=500&auto=format&fit=crop",
             "Freshly baked whole wheat bread"),
            ("Organic Carrots", "Produce", 1.49, 200,
             "https://images.unsplash.com/photo-1447518352343-13983f90e552?q=80&w=500&auto=format&fit=crop",
             "Crisp organic carrots, perfect for salads"),
            ("Greek Yogurt", "Dairy", 4.99, 100,
             "https://images.unsplash.com/photo-1488477181946-6428a0291840?q=80&w=500&auto=format&fit=crop",
             "Creamy Greek yogurt, high protein content"),
            ("Almond Butter", "Pantry", 7.99, 50,
             "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=500&auto=format&fit=crop",
             "Natural almond butter with no added sugar"),
            ("Free-Range Eggs", "Dairy", 5.49, 120,
             "https://images.unsplash.com/photo-1578295272aca8206b6f1fb76f80f3d7a4e8f36?q=80&w=500&auto=format&fit=crop",
             "A dozen free-range eggs from local farms"),
            ("Cherry Tomatoes", "Produce", 3.49, 100,
             "https://images.unsplash.com/photo-1592075162160-e4fee6f67457?q=80&w=500&auto=format&fit=crop",
             "Sweet cherry tomatoes, perfect for salads"),
            ("Whole Grain Pasta", "Pantry", 2.29, 200,
             "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=500&auto=format&fit=crop",
             "Whole grain pasta, rich in fiber"),
            ("Organic Apple", "Produce", 0.99, 250,
             "https://images.unsplash.com/photo-1560806e4b1eba20e7f3b76eba5d68e8?q=80&w=500&auto=format&fit=crop",
             "Crisp, juicy organic apples"),
            ("Cheddar Cheese", "Dairy", 6.99, 75,
             "https://images.unsplash.com/photo-1555939594-58d7cb561537?q=80&w=500&auto=format&fit=crop",
             "Aged sharp cheddar cheese"),
            ("Spinach", "Produce", 2.99, 80,
             "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=500&auto=format&fit=crop",
             "Fresh baby spinach, packed with nutrients"),
            ("Salmon Fillet", "Seafood", 12.99, 40,
             "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=500&auto=format&fit=crop",
             "Wild-caught salmon fillets"),
            ("Brown Rice", "Pantry", 3.49, 150,
             "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=500&auto=format&fit=crop",
             "Long-grain brown rice, nutty flavor"),
            ("Blueberries", "Produce", 4.99, 60,
             "https://images.unsplash.com/photo-1599599810694-a5f899da9e47?q=80&w=500&auto=format&fit=crop",
             "Fresh blueberries, antioxidant-rich"),
            ("Olive Oil", "Pantry", 9.99, 40,
             "https://images.unsplash.com/photo-1502224311726-72d15d3c5c16?q=80&w=500&auto=format&fit=crop",
             "Extra virgin olive oil from Italy"),
            ("Croissants", "Bakery", 3.99, 30,
             "https://images.unsplash.com/photo-1585854870192-e5cd83cf7b73?q=80&w=500&auto=format&fit=crop",
             "Buttery French croissants"),
            ("Avocados", "Produce", 1.99, 120,
             "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?q=80&w=500&auto=format&fit=crop",
             "Ripe, creamy avocados"),
            ("Whole Wheat Cereal", "Pantry", 4.49, 90,
             "https://images.unsplash.com/photo-1585518895894-94ccb9e9b3b6?q=80&w=500&auto=format&fit=crop",
             "Nutritious whole wheat cereal"),
            ("Fresh Broccoli", "Produce", 2.49, 110,
             "https://images.unsplash.com/photo-1447518352343-13983f90e552?q=80&w=500&auto=format&fit=crop",
             "Vibrant green broccoli crowns"),
        ]

        cur.executemany(
            "INSERT INTO products (name, category, price, stock, img_url, description) VALUES (?, ?, ?, ?, ?, ?)",
            products_data
        )

    conn.commit()
    conn.close()


init_db()


# ============ AUTH ROUTES ============

@app.route('/')
def index():
    if 'user' in session:
        if session.get('role') == 'Admin' or session.get('role') == 'Cashier':
            return redirect('/admin-portal')
        else:
            return redirect('/customer')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {username}!', 'success')

            if user['role'] in ['Admin', 'Cashier']:
                return redirect('/admin-portal')
            else:
                return redirect('/customer')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect('/signup')

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), 'Customer')
            )
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and user['role'] in ['Admin', 'Cashier'] and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["role"]}!', 'success')
            return redirect('/admin-portal')
        else:
            flash('Unauthorized access or invalid credentials', 'danger')

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/login')


# ============ CUSTOMER ROUTES ============

@app.route('/customer')
def customer():
    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'Customer':
        return redirect('/admin-portal')

    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template('customer.html', products=products)


@app.route('/cart')
def cart():
    if 'user' not in session or session.get('role') != 'Customer':
        return redirect('/login')

    cart_items = session.get('cart', {})

    conn = get_db()
    products = {str(p['id']): p for p in conn.execute("SELECT * FROM products").fetchall()}
    conn.close()

    cart_data = []
    total = 0

    for product_id, quantity in cart_items.items():
        if product_id in products:
            product = products[product_id]
            item_total = product['price'] * quantity
            cart_data.append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'total': item_total
            })
            total += item_total

    return render_template('cart.html', cart=cart_data, total=total)


@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session or session.get('role') != 'Customer':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    if 'cart' not in session:
        session['cart'] = {}

    if product_id in session['cart']:
        session['cart'][product_id] += quantity
    else:
        session['cart'][product_id] = quantity

    session.modified = True

    return jsonify({'success': True, 'cart_count': sum(session['cart'].values())})


@app.route('/api/remove-from-cart/<product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    if 'user' not in session or session.get('role') != 'Customer':
        return jsonify({'error': 'Unauthorized'}), 401

    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True

    return jsonify({'success': True})


@app.route('/api/update-cart-quantity', methods=['POST'])
def update_cart_quantity():
    if 'user' not in session or session.get('role') != 'Customer':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    if 'cart' in session and product_id in session['cart']:
        if quantity <= 0:
            del session['cart'][product_id]
        else:
            session['cart'][product_id] = quantity
        session.modified = True

    return jsonify({'success': True})


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session or session.get('role') != 'Customer':
        return redirect('/login')

    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect('/cart')

    conn = get_db()
    products = {str(p['id']): p for p in conn.execute("SELECT * FROM products").fetchall()}

    total_amount = 0
    order_items = []

    for product_id, quantity in cart_items.items():
        if product_id in products:
            product = products[product_id]
            item_total = product['price'] * quantity
            total_amount += item_total
            order_items.append({
                'product_id': int(product_id),
                'quantity': quantity,
                'price_at_purchase': product['price']
            })

    # Create order
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_username, total_amount, status, order_date) VALUES (?, ?, ?, ?)",
        (session['user'], total_amount, 'Pending', order_date)
    )
    conn.commit()

    order_id = cur.lastrowid

    # Add order items
    for item in order_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
            (order_id, item['product_id'], item['quantity'], item['price_at_purchase'])
        )

    conn.commit()
    conn.close()

    # Clear cart
    session['cart'] = {}
    session.modified = True

    flash('Order placed successfully!', 'success')
    return redirect(f'/order-confirmation/{order_id}')


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user' not in session or session.get('role') != 'Customer':
        return redirect('/login')

    conn = get_db()
    order = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND customer_username = ?",
        (order_id, session['user'])
    ).fetchone()

    if not order:
        flash('Order not found', 'danger')
        return redirect('/customer')

    order_items = conn.execute(
        "SELECT oi.*, p.name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
        (order_id,)
    ).fetchall()

    conn.close()

    return render_template('order_confirmation.html', order=order, order_items=order_items)


# ============ ADMIN/CASHIER ROUTES ============

@app.route('/admin-portal')
def admin_portal():
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return redirect('/admin-login')

    conn = get_db()

    # Get stats
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    # Get recent orders
    orders = conn.execute("""
                          SELECT *
                          FROM orders
                          ORDER BY order_date DESC LIMIT 10
                          """).fetchall()

    conn.close()

    return render_template('admin.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_products=total_products,
                           orders=orders)


@app.route('/admin/inventory')
def admin_inventory():
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return redirect('/admin-login')

    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    return render_template('inventory.html', products=products)


@app.route('/admin/api/add-product', methods=['POST'])
def api_add_product():
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO products (name, category, price, stock, img_url, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (data['name'], data['category'], data['price'], data['stock'], data['img_url'], data['description']))
    conn.commit()
    product_id = cur.lastrowid
    conn.close()

    return jsonify({'success': True, 'product_id': product_id})


@app.route('/admin/api/update-product/<int:product_id>', methods=['POST'])
def api_update_product(product_id):
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()

    conn = get_db()
    conn.execute("""
                 UPDATE products
                 SET name=?,
                     category=?,
                     price=?,
                     stock=?,
                     img_url=?,
                     description=?
                 WHERE id = ?
                 """,
                 (data['name'], data['category'], data['price'], data['stock'], data['img_url'], data['description'],
                  product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/admin/api/update-stock/<int:product_id>', methods=['POST'])
def api_update_stock(product_id):
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    stock = data.get('stock')

    conn = get_db()
    conn.execute("UPDATE products SET stock=? WHERE id=?", (stock, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/admin/api/update-order-status/<int:order_id>', methods=['POST'])
def api_update_order_status(order_id):
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    status = data.get('status')

    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/admin/orders')
def admin_orders():
    if 'user' not in session or session.get('role') not in ['Admin', 'Cashier']:
        return redirect('/admin-login')

    conn = get_db()
    orders = conn.execute("""
                          SELECT *
                          FROM orders
                          ORDER BY order_date DESC
                          """).fetchall()
    conn.close()

    return render_template('orders.html', orders=orders)


if __name__ == '__main__':
    app.run(debug=True)
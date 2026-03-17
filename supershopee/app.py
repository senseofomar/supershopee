from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
from datetime import datetime
from database import init_db, DB_PATH

app = Flask(__name__)
app.secret_key = "supershopee_secret_key_2026"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


init_db()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============ AUTHENTICATION ROUTES ============

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session["user"] = username
            session["role"] = user['role']

            if user['role'] == 'Admin':
                return redirect("/admin")
            elif user['role'] == 'Cashier':
                return redirect("/admin")
            elif user['role'] == 'Staff':
                return redirect("/staff/products")
            else:
                return redirect("/customer")

        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, generate_password_hash(password), 'Customer'))
            conn.commit()
            conn.close()
            # Redirect to login, not show message on customer page
            return redirect("/?signup_success=true")
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", error="Username already exists")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ============ CUSTOMER ROUTES ============

@app.route("/customer")
def customer():
    if session.get("role") != "Customer":
        return redirect("/")

    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY category").fetchall()
    conn.close()

    return render_template("customer.html", products=products)


@app.route("/cart")
def cart():
    if session.get("role") != "Customer":
        return redirect("/")

    cart_items = session.get('cart', {})
    conn = get_db()
    products_dict = {str(p['id']): p for p in conn.execute("SELECT * FROM products").fetchall()}
    conn.close()

    cart_data = []
    total = 0

    for product_id, quantity in cart_items.items():
        if product_id in products_dict:
            product = products_dict[product_id]
            item_total = float(product['price']) * int(quantity)
            cart_data.append({
                'id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'total': item_total
            })
            total += item_total

    return render_template("cart.html", cart=cart_data, total=total)


@app.route("/api/add-to-cart", methods=["POST"])
def add_to_cart():
    if session.get("role") != "Customer":
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
    return jsonify({'success': True})


@app.route("/api/remove-from-cart/<product_id>", methods=["DELETE"])
def remove_from_cart(product_id):
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True

    return jsonify({'success': True})


@app.route("/api/update-cart-quantity", methods=["POST"])
def update_cart_quantity():
    if session.get("role") != "Customer":
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


@app.route("/checkout", methods=["POST"])
def checkout():
    if session.get("role") != "Customer":
        return redirect("/")

    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect('/cart')

    conn = get_db()
    products_dict = {str(p['id']): p for p in conn.execute("SELECT * FROM products").fetchall()}

    total_amount = 0
    order_items = []

    for product_id, quantity in cart_items.items():
        if product_id in products_dict:
            product = products_dict[product_id]
            item_total = float(product['price']) * int(quantity)
            total_amount += item_total
            order_items.append({
                'product_id': int(product_id),
                'quantity': int(quantity),
                'price_at_purchase': float(product['price'])
            })

    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_username, total_amount, status, order_date) VALUES (?, ?, ?, ?)",
        (session['user'], total_amount, 'Pending', order_date)
    )
    conn.commit()

    order_id = cur.lastrowid

    for item in order_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
            (order_id, item['product_id'], item['quantity'], item['price_at_purchase'])
        )

    conn.commit()
    conn.close()

    session['cart'] = {}
    session.modified = True

    flash('Order placed successfully!', 'success')
    return redirect(f'/order-confirmation/{order_id}')


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    if session.get("role") != "Customer":
        return redirect("/")

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

@app.route("/admin")
def admin():
    if session.get("role") not in ['Admin', 'Cashier']:
        return redirect("/")

    conn = get_db()

    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_revenue = conn.execute("SELECT SUM(total_amount) FROM orders WHERE status = 'Completed'").fetchone()[0] or 0

    orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC LIMIT 10").fetchall()
    products = conn.execute("SELECT * FROM products ORDER BY category").fetchall()
    conn.close()

    return render_template('admin.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_products=total_products,
                           total_revenue=total_revenue,
                           orders=orders,
                           products=products)


@app.route("/admin/inventory")
def admin_inventory():
    if session.get("role") not in ['Admin', 'Cashier']:
        return redirect("/")

    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY category").fetchall()
    conn.close()

    return render_template('inventory.html', products=products)


@app.route("/admin/orders")
def admin_orders():
    if session.get("role") not in ['Admin', 'Cashier']:
        return redirect("/")

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC").fetchall()
    conn.close()

    return render_template('orders.html', orders=orders)


@app.route("/admin/api/update-product-stock/<int:product_id>", methods=["POST"])
def api_update_stock(product_id):
    if session.get("role") not in ['Admin', 'Cashier', 'Staff']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    stock = int(data.get('stock', 0))

    conn = get_db()
    conn.execute("UPDATE products SET stock=? WHERE id=?", (stock, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/admin/api/update-product-price/<int:product_id>", methods=["POST"])
def api_update_price(product_id):
    if session.get("role") not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    price = float(data.get('price', 0))

    conn = get_db()
    conn.execute("UPDATE products SET price=? WHERE id=?", (price, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/admin/api/update-order-status/<int:order_id>", methods=["POST"])
def api_update_order_status(order_id):
    if session.get("role") not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    status = data.get('status')

    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


# ============ STAFF ROUTES ============

@app.route("/staff/products")
def staff_products():
    if session.get("role") != "Staff":
        return redirect("/")

    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY category").fetchall()
    conn.close()

    return render_template('staff_products.html', products=products)


@app.route("/admin/api/add-product", methods=["POST"])
def api_add_product():
    if session.get("role") not in ['Admin', 'Staff']:
        return jsonify({'error': 'Unauthorized'}), 401

    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 0))
    description = request.form.get('description', '')

    img_filename = ""
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img_filename = f"prod_{random.randint(1000, 9999)}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            img_filename = f"uploads/{img_filename}"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO products (name, category, price, stock, img_url, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (name, category, price, stock, img_filename, description))
    conn.commit()
    product_id = cur.lastrowid
    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'product_id': product_id})
    else:
        flash('Product added successfully!', 'success')
        return redirect('/staff/products')


@app.route("/admin/api/delete-product/<int:product_id>", methods=["POST"])
def api_delete_product(product_id):
    if session.get("role") not in ['Admin', 'Staff']:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True)
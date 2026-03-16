from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from database import init_db, DB_PATH

app = Flask(__name__)
app.secret_key = "supershopee_secret_key_2026"

# Configuration for Image Uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


init_db()


# --- AUTHENTICATION ROUTES ---

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

            if user['role'] in ['Admin', 'Cashier']:
                return redirect("/admin")
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
            return render_template("signup.html", error="Passwords do not match. Please try again.")

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, generate_password_hash(password), 'Customer'))
            conn.commit()
            flash("Account created successfully! Please log in.")
            return redirect("/")
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Username already exists")
        finally:
            conn.close()

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND role IN ('Admin', 'Cashier')",
                            (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session["user"] = username
            session["role"] = user['role']
            return redirect("/admin")

        return render_template("admin_login.html", error="Authentication failed.")

    return render_template("admin_login.html")


# --- CUSTOMER ROUTES ---

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
    return jsonify({'success': True, 'cart_count': sum(session['cart'].values())})


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


# --- ADMIN/CASHIER ROUTES ---

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
    conn.close()

    return render_template('admin.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_products=total_products,
                           total_revenue=total_revenue,
                           orders=orders)


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
    if session.get("role") not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    stock = int(data.get('stock', 0))

    conn = get_db()
    conn.execute("UPDATE products SET stock=? WHERE id=?", (stock, product_id))
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

    return jsonify({'success': True, 'new_status': status})


@app.route("/admin/api/add-product", methods=["POST"])
def api_add_product():
    if session.get("role") not in ['Admin', 'Cashier']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO products (name, category, price, stock, img_url, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (data['name'], data['category'], data['price'], data['stock'], data.get('img_url', ''),
                      data['description']))
    conn.commit()
    product_id = cur.lastrowid
    conn.close()

    return jsonify({'success': True, 'product_id': product_id})


if __name__ == "__main__":
    app.run(debug=True)
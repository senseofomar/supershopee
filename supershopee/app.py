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


# ============ AUTH ROUTES ============

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

        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters")

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, generate_password_hash(password), 'Customer'))
            conn.commit()
            flash("Account created! Please log in.", 'success')
            return redirect("/")
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Username already exists")
        finally:
            conn.close()

    return render_template("signup.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND role='Admin'", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session["user"] = username
            session["role"] = 'Admin'
            return redirect("/admin")

        return render_template("admin_login.html", error="Invalid admin credentials")
    return render_template("admin_login.html")


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
    products = conn.execute("SELECT * FROM products WHERE is_active=1 ORDER BY category").fetchall()
    conn.close()

    return render_template("customer.html", products=products)


@app.route("/my-orders")
def my_orders():
    if session.get("role") != "Customer":
        return redirect("/")

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders WHERE customer_username=? ORDER BY order_date DESC",
                          (session['user'],)).fetchall()
    conn.close()

    return render_template("my_orders.html", orders=orders)

@app.route("/cart")
def cart():
    if session.get("role") != "Customer":
        return redirect("/")

    conn = get_db()
    cart_items = conn.execute(
        "SELECT ci.id, ci.product_id, ci.quantity, p.name, p.price FROM cart_items ci "
        "JOIN products p ON ci.product_id = p.id WHERE ci.customer_username=?",
        (session['user'],)
    ).fetchall()
    conn.close()

    cart_data = []
    total = 0
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        cart_data.append({
            'id': item['id'],
            'product_id': item['product_id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })
        total += item_total

    return render_template("cart.html", cart=cart_data, total=total)


@app.route("/api/add-to-cart", methods=["POST"])
def add_to_cart():
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    product_id = int(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    conn = get_db()

    # Check if product exists
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Check if already in cart
    existing = conn.execute(
        "SELECT * FROM cart_items WHERE customer_username=? AND product_id=?",
        (session['user'], product_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE cart_items SET quantity=quantity+? WHERE customer_username=? AND product_id=?",
            (quantity, session['user'], product_id)
        )
    else:
        conn.execute(
            "INSERT INTO cart_items (customer_username, product_id, quantity) VALUES (?, ?, ?)",
            (session['user'], product_id, quantity)
        )

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/api/remove-from-cart/<int:cart_item_id>", methods=["DELETE"])
def remove_from_cart(cart_item_id):
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    conn.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/api/update-cart-quantity", methods=["POST"])
def update_cart_quantity():
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    cart_item_id = int(data.get('cart_item_id'))
    quantity = int(data.get('quantity', 1))

    conn = get_db()
    if quantity <= 0:
        conn.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
    else:
        conn.execute("UPDATE cart_items SET quantity=? WHERE id=?", (quantity, cart_item_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/checkout", methods=["POST"])
def checkout():
    if session.get("role") != "Customer":
        return redirect("/")

    conn = get_db()
    cart_items = conn.execute(
        "SELECT ci.product_id, ci.quantity, p.name, p.price FROM cart_items ci "
        "JOIN products p ON ci.product_id = p.id WHERE ci.customer_username=?",
        (session['user'],)
    ).fetchall()

    if not cart_items:
        conn.close()
        flash('Your cart is empty', 'warning')
        return redirect('/cart')

    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_username, total_amount, status, order_date) VALUES (?, ?, ?, ?)",
        (session['user'], total_amount, 'Pending', order_date)
    )
    conn.commit()
    order_id = cur.lastrowid

    for item in cart_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_name, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
            (order_id, item['name'], item['quantity'], item['price'])
        )

    conn.execute("DELETE FROM cart_items WHERE customer_username=?", (session['user'],))
    conn.commit()
    conn.close()

    flash('Order placed successfully!', 'success')
    return redirect(f'/order-confirmation/{order_id}')


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    if session.get("role") != "Customer":
        return redirect("/")

    conn = get_db()
    order = conn.execute(
        "SELECT * FROM orders WHERE id=? AND customer_username=?",
        (order_id, session['user'])
    ).fetchone()

    if not order:
        return redirect('/customer')

    order_items = conn.execute(
        "SELECT * FROM order_items WHERE order_id=?",
        (order_id,)
    ).fetchall()

    conn.close()

    return render_template('order_confirmation.html', order=order, order_items=order_items)


# ============ ADMIN ROUTES ============

@app.route("/admin")
def admin():
    if session.get("role") != 'Admin':
        return redirect("/")

    conn = get_db()

    stats = {
        'total_orders': conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        'pending_orders': conn.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'").fetchone()[0],
        'total_products': conn.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0],
        'total_revenue': conn.execute("SELECT SUM(total_amount) FROM orders WHERE status='Completed'").fetchone()[
                             0] or 0
    }

    orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC LIMIT 10").fetchall()

    # Fetch all non-admin users to display in the dashboard
    users = conn.execute("SELECT * FROM users WHERE role != 'Admin' ORDER BY id DESC").fetchall()
    conn.close()

    return render_template('admin.html', stats=stats, orders=orders, users=users)


@app.route("/admin/inventory")
def admin_inventory():
    if session.get("role") != 'Admin':
        return redirect("/")

    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY category").fetchall()
    conn.close()

    return render_template('inventory.html', products=products)


@app.route("/admin/orders")
def admin_orders():
    if session.get("role") != 'Admin':
        return redirect("/")

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC").fetchall()
    conn.close()

    return render_template('orders.html', orders=orders)


@app.route("/admin/api/add-product", methods=["POST"])
def admin_add_product():
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 0))
    description = request.form.get('description', '')

    img_url = ""
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img_filename = f"prod_{random.randint(1000, 9999)}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
            img_url = img_filename

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, category, price, stock, img_url, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, category, price, stock, img_url, description, 1)
    )
    conn.commit()
    conn.close()

    flash('Product added successfully!', 'success')
    return redirect('/admin/inventory')


@app.route("/admin/api/update-product-stock/<int:product_id>", methods=["POST"])
def admin_update_stock(product_id):
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    stock = int(data.get('stock', 0))

    conn = get_db()
    conn.execute("UPDATE products SET stock=? WHERE id=?", (stock, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/admin/api/update-product-price/<int:product_id>", methods=["POST"])
def admin_update_price(product_id):
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    price = float(data.get('price', 0))

    conn = get_db()
    conn.execute("UPDATE products SET price=? WHERE id=?", (price, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/admin/api/delete-product/<int:product_id>", methods=["POST"])
def admin_delete_product(product_id):
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    conn.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route("/admin/api/update-order-status/<int:order_id>", methods=["POST"])
def admin_update_order_status(order_id):
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    status = data.get('status')

    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route("/admin/api/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    # Delete the user securely
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True)
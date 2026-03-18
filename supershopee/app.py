from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
from datetime import datetime
from database import init_db, DB_PATH

# ============ INITIALIZATION ============
app = Flask(__name__)
app.secret_key = "supershopee_secret_key_2026"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()


# ============ HELPER FUNCTIONS ============

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def validate_input(value, input_type='text', min_length=1, max_length=255):
    """Validate user input"""
    if not value:
        return False
    if input_type == 'email':
        return '@' in value and '.' in value
    if input_type == 'number':
        try:
            float(value)
            return True
        except:
            return False
    return len(str(value)) >= min_length and len(str(value)) <= max_length


def format_currency(amount):
    """Format amount as currency"""
    try:
        return "%.2f" % float(amount)
    except:
        return "0.00"


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error_404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error_500.html'), 500


# ============ AUTH ROUTES ============

@app.route("/", methods=["GET", "POST"])
def login():
    """Customer login"""
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                return render_template("login.html", error="Username and password required")

            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session["user"] = username
                session["role"] = user['role']

                if user['role'] == 'Admin':
                    flash("Welcome back, Admin!", 'success')
                    return redirect("/admin")
                else:
                    flash(f"Welcome {username}!", 'success')
                    return redirect("/customer")

            return render_template("login.html", error="Invalid credentials")
        except Exception as e:
            return render_template("login.html", error="An error occurred during login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Customer signup"""
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            # Validation
            if not username or not password:
                return render_template("signup.html", error="Username and password required")

            if not validate_input(username, min_length=3, max_length=30):
                return render_template("signup.html", error="Username must be 3-30 characters")

            if password != confirm_password:
                return render_template("signup.html", error="Passwords do not match")

            if len(password) < 6:
                return render_template("signup.html", error="Password must be at least 6 characters")

            if len(password) > 100:
                return render_template("signup.html", error="Password too long")

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

        except Exception as e:
            return render_template("signup.html", error="An error occurred during signup")

    return render_template("signup.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    """Admin login"""
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                return render_template("admin_login.html", error="Username and password required")

            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE username=? AND role='Admin'", (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session["user"] = username
                session["role"] = 'Admin'
                flash("Admin login successful!", 'success')
                return redirect("/admin")

            return render_template("admin_login.html", error="Invalid admin credentials")
        except Exception as e:
            return render_template("admin_login.html", error="An error occurred during login")

    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    """Logout"""
    session.clear()
    flash("Logged out successfully!", 'success')
    return redirect("/")


# ============ CUSTOMER ROUTES ============

@app.route("/customer")
def customer():
    """Browse products"""
    if session.get("role") != "Customer":
        return redirect("/")

    try:
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()

        conn = get_db()

        # Build query
        query = "SELECT * FROM products WHERE is_active=1"
        params = []

        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY category, name"

        products = conn.execute(query, params).fetchall()

        # Get categories for filter dropdown
        categories = conn.execute(
            "SELECT DISTINCT category FROM products WHERE is_active=1 ORDER BY category").fetchall()

        conn.close()

        return render_template("customer.html", products=products, categories=categories, search=search,
                               selected_category=category)
    except Exception as e:
        flash("Error loading products", 'danger')
        return redirect("/")


@app.route("/my-orders")
def my_orders():
    """View customer orders"""
    if session.get("role") != "Customer":
        return redirect("/")

    try:
        conn = get_db()
        orders = conn.execute(
            "SELECT * FROM orders WHERE customer_username=? ORDER BY order_date DESC",
            (session['user'],)
        ).fetchall()
        conn.close()

        return render_template("my_orders.html", orders=orders)
    except Exception as e:
        flash("Error loading orders", 'danger')
        return redirect("/customer")


@app.route("/cart")
def cart():
    """View shopping cart"""
    if session.get("role") != "Customer":
        return redirect("/")

    try:
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
    except Exception as e:
        flash("Error loading cart", 'danger')
        return redirect("/customer")


@app.route("/api/add-to-cart", methods=["POST"])
def add_to_cart():
    """Add product to cart"""
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        product_id = int(data.get('product_id', 0))
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return jsonify({'error': 'Invalid quantity'}), 400

        conn = get_db()

        # Check if product exists and is active
        product = conn.execute("SELECT * FROM products WHERE id=? AND is_active=1", (product_id,)).fetchone()
        if not product:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        # Check stock
        if product['stock'] < quantity:
            conn.close()
            return jsonify({'error': 'Insufficient stock'}), 400

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

        return jsonify({'success': True, 'message': f'{product["name"]} added to cart!'})
    except Exception as e:
        return jsonify({'error': 'Error adding to cart'}), 500


@app.route("/api/remove-from-cart/<int:cart_item_id>", methods=["DELETE"])
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        conn.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error removing from cart'}), 500


@app.route("/api/update-cart-quantity", methods=["POST"])
def update_cart_quantity():
    """Update cart item quantity"""
    if session.get("role") != "Customer":
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        cart_item_id = int(data.get('cart_item_id', 0))
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return jsonify({'error': 'Invalid quantity'}), 400

        conn = get_db()
        if quantity <= 0:
            conn.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
        else:
            conn.execute("UPDATE cart_items SET quantity=? WHERE id=?", (quantity, cart_item_id))

        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error updating cart'}), 500


@app.route("/checkout", methods=["POST"])
def checkout():
    """Checkout and place order"""
    if session.get("role") != "Customer":
        return redirect("/")

    try:
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

        # Calculate total
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create order
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_username, total_amount, status, order_date) VALUES (?, ?, ?, ?)",
            (session['user'], total_amount, 'Pending', order_date)
        )
        conn.commit()
        order_id = cur.lastrowid

        # Add order items
        for item in cart_items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_name, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                (order_id, item['name'], item['quantity'], item['price'])
            )

        # Clear cart
        conn.execute("DELETE FROM cart_items WHERE customer_username=?", (session['user'],))
        conn.commit()
        conn.close()

        flash('Order placed successfully!', 'success')
        return redirect(f'/order-confirmation/{order_id}')
    except Exception as e:
        flash('Error during checkout', 'danger')
        return redirect('/cart')


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    if session.get("role") != "Customer":
        return redirect("/")

    try:
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
    except Exception as e:
        flash('Error loading order', 'danger')
        return redirect('/customer')


# ============ ADMIN ROUTES ============

@app.route("/admin")
def admin():
    """Admin dashboard"""
    if session.get("role") != 'Admin':
        return redirect("/")

    try:
        conn = get_db()

        # Get statistics
        stats = {
            'total_orders': conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            'pending_orders': conn.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'").fetchone()[0],
            'total_products': conn.execute("SELECT COUNT(*) FROM products WHERE is_active=1").fetchone()[0],
            'total_revenue': conn.execute("SELECT SUM(total_amount) FROM orders WHERE status='Completed'").fetchone()[
                                 0] or 0,
            'low_stock_products':
                conn.execute("SELECT COUNT(*) FROM products WHERE stock < 50 AND is_active=1").fetchone()[0]
        }

        orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC LIMIT 10").fetchall()
        users = conn.execute("SELECT * FROM users WHERE role != 'Admin' ORDER BY id DESC").fetchall()

        conn.close()

        return render_template('admin.html', stats=stats, orders=orders, users=users)
    except Exception as e:
        flash('Error loading dashboard', 'danger')
        return redirect("/")


@app.route("/admin/inventory")
def admin_inventory():
    """Inventory management"""
    if session.get("role") != 'Admin':
        return redirect("/")

    try:
        conn = get_db()
        products = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
        conn.close()

        return render_template('inventory.html', products=products)
    except Exception as e:
        flash('Error loading inventory', 'danger')
        return redirect("/admin")


@app.route("/admin/orders")
def admin_orders():
    """Order management"""
    if session.get("role") != 'Admin':
        return redirect("/")

    try:
        conn = get_db()
        orders = conn.execute("SELECT * FROM orders ORDER BY order_date DESC").fetchall()
        conn.close()

        return render_template('orders.html', orders=orders)
    except Exception as e:
        flash('Error loading orders', 'danger')
        return redirect("/admin")


@app.route("/admin/api/add-product", methods=["POST"])
def admin_add_product():
    """Add new product"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        price = request.form.get('price', '0')
        stock = request.form.get('stock', '0')
        description = request.form.get('description', '').strip()

        # Validation
        if not name or not category:
            flash('Product name and category required', 'danger')
            return redirect('/admin/inventory')

        if not validate_input(price, 'number') or float(price) < 0:
            flash('Invalid price', 'danger')
            return redirect('/admin/inventory')

        if not validate_input(stock, 'number') or int(stock) < 0:
            flash('Invalid stock', 'danger')
            return redirect('/admin/inventory')

        price = float(price)
        stock = int(stock)

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

        flash(f'Product "{name}" added successfully!', 'success')
        return redirect('/admin/inventory')
    except Exception as e:
        flash('Error adding product', 'danger')
        return redirect('/admin/inventory')


@app.route("/admin/api/update-product-stock/<int:product_id>", methods=["POST"])
def admin_update_stock(product_id):
    """Update product stock"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        stock = int(data.get('stock', 0))

        if stock < 0:
            return jsonify({'error': 'Invalid stock'}), 400

        conn = get_db()
        conn.execute("UPDATE products SET stock=? WHERE id=?", (stock, product_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error updating stock'}), 500


@app.route("/admin/api/update-product-price/<int:product_id>", methods=["POST"])
def admin_update_price(product_id):
    """Update product price"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        price = float(data.get('price', 0))

        if price < 0:
            return jsonify({'error': 'Invalid price'}), 400

        conn = get_db()
        conn.execute("UPDATE products SET price=? WHERE id=?", (price, product_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error updating price'}), 500


@app.route("/admin/api/delete-product/<int:product_id>", methods=["POST"])
def admin_delete_product(product_id):
    """Delete product (soft delete)"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        conn.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error deleting product'}), 500


@app.route("/admin/api/update-order-status/<int:order_id>", methods=["POST"])
def admin_update_order_status(order_id):
    """Update order status"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        status = data.get('status', '').strip()

        if status not in ['Pending', 'Completed', 'Cancelled']:
            return jsonify({'error': 'Invalid status'}), 400

        conn = get_db()
        conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error updating order'}), 500


@app.route("/admin/api/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    """Delete user"""
    if session.get("role") != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db()
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Error deleting user'}), 500


# ============ RUN APP ============

if __name__ == "__main__":
    app.run(debug=True)
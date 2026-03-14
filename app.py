from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a proper secret key

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, quantity INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, total REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER)''')

    # Seed admin and 20 products
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', generate_password_hash('adminpass')))
    for i in range(1, 21):
        cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (f'Product {i}', i * 10, 100))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Fetch products and display
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        pass
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup logic
        pass
    return render_template('signup.html')

@app.route('/cart')
def cart():
    # Handle cart display and logic
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Handle order creation
    return render_template('checkout.html')

@app.route('/admin')
def admin():
    # Admin dashboard
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
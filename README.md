# 🛒 Super Shopee - E-Commerce & POS System

A modern, fully-functional supermarket e-commerce and point-of-sale system built with Flask and SQLite. Features complete customer shopping experience, admin dashboard, and inventory management.

## ✨ Features

### 👥 **For Customers**
- Browse products by category (Dairy, Fruits, Vegetables, Bakery, Pantry, Beverages)
- Add items to cart with quantity management
- Checkout and place orders
- View complete order history
- Real-time cart notifications
- Responsive mobile-friendly interface

### 🛠️ **For Admins**
- Dashboard with KPIs (total orders, revenue, pending orders, active products)
- Inventory management (add, update, delete products)
- Order management and status updates
- User management with role-based access
- Real-time stock tracking
- Sales analytics

### 🔐 **Security**
- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control (Admin/Customer)
- SQL injection prevention with parameterized queries
- Secure file uploads for product images

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/senseofomar/supershopee.git
   cd supershopee
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   cd supershopee
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🔑 Default Credentials

### Admin Access
- **Username:** `admin`
- **Password:** `admin123`
- **Access:** Admin Dashboard, Inventory Management, Order Management

### Test Customer
- **Username:** `shopper`
- **Password:** `shopper123`
- **Access:** Customer Dashboard, Shopping, Order History

### Create Your Own Account
Visit the signup page to create a customer account.

## 📁 Project Structure

```
supershopee/
├── app.py                      # Main Flask application
├── database.py                 # Database initialization & seeding
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── static/
│   ├── style.css              # Main stylesheet
│   ├── uploads/               # Product image uploads
│   └── .gitkeep               # Keep uploads folder in git
└── templates/
    ├── layout.html            # Base template with navigation
    ├── login.html             # Customer login page
    ├── signup.html            # Customer signup page
    ├── admin_login.html       # Admin login page
    ├── customer.html          # Product browsing page
    ├── cart.html              # Shopping cart page
    ├── checkout.html          # Checkout page
    ├── order_confirmation.html # Order confirmation page
    ├── order_history.html     # Customer order history
    ├── admin.html             # Admin dashboard
    ├── inventory.html         # Inventory management
    ├── orders.html            # Order management
    ├── my_orders.html         # Customer my orders
    ├── admin_login.html       # Admin access portal
    └── error_404.html         # 404 error page
```

## 🎨 Key Features

### Product Categories
- **Dairy:** Milk, Yogurt, Cheese, Paneer, Butter
- **Fruits:** Bananas, Apples, Oranges, Strawberries, Grapes
- **Vegetables:** Potatoes, Onions, Tomatoes, Carrots, Broccoli
- **Bakery:** Bread, Croissants, Cookies
- **Pantry:** Rice, Pasta, Olive Oil, Almonds, Honey
- **Beverages:** Coffee, Tea

### Admin Features
- View real-time sales metrics
- Manage product inventory (add/update/delete)
- Track order statuses
- User management
- Stock level monitoring

### Customer Features
- Smart product search and filtering
- One-click add to cart
- Secure checkout process
- Complete order history
- Order status tracking

## 🧪 Testing Checklist

- [x] All pages load without errors
- [x] Login/signup work for all roles
- [x] Customer can browse and add products to cart
- [x] Checkout creates order successfully
- [x] Admin can view and manage inventory
- [x] Admin can update order statuses
- [x] Modals and toasts work smoothly
- [x] Responsive on mobile/tablet/desktop
- [x] All images load correctly
- [x] No console errors
- [x] No template syntax errors

## 📊 Database Schema

### Users Table
```sql
id | username | password | role
```

### Products Table
```sql
id | name | category | price | stock | img_url | description | is_active
```

### Orders Table
```sql
id | customer_username | total_amount | status | order_date
```

### Order Items Table
```sql
id | order_id | product_name | quantity | price_at_purchase
```

### Cart Items Table
```sql
id | customer_username | product_id | quantity
```

## 🎯 API Endpoints

### Authentication
- `POST /` - Customer Login
- `POST /signup` - Customer Signup
- `POST /admin-login` - Admin Login
- `GET /logout` - Logout

### Customer Routes
- `GET /customer` - Browse products
- `GET /cart` - View shopping cart
- `GET /my-orders` - View order history
- `GET /order-confirmation/<id>` - Order details

### Customer APIs
- `POST /api/add-to-cart` - Add product to cart
- `DELETE /api/remove-from-cart/<id>` - Remove from cart
- `POST /api/update-cart-quantity` - Update quantity
- `POST /checkout` - Place order

### Admin Routes
- `GET /admin` - Dashboard
- `GET /admin/inventory` - Inventory management
- `GET /admin/orders` - Order management

### Admin APIs
- `POST /admin/api/add-product` - Add product
- `POST /admin/api/update-product-stock/<id>` - Update stock
- `POST /admin/api/update-product-price/<id>` - Update price
- `POST /admin/api/delete-product/<id>` - Delete product
- `POST /admin/api/update-order-status/<id>` - Update order status
- `POST /admin/api/delete-user/<id>` - Delete user

## 🛡️ Security Features

1. **Password Security**
   - Passwords hashed using Werkzeug
   - Minimum 6 characters required

2. **Session Management**
   - Secure session tokens
   - Role-based access control
   - Automatic session expiration

3. **Data Protection**
   - SQL injection prevention with parameterized queries
   - Input validation on all forms
   - Secure file upload handling

4. **Access Control**
   - Role-based route protection
   - Admin-only endpoints secured
   - Customer data isolation

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
cd supershopee
python database.py
```

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

### Dependencies Not Installing
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📈 Performance Optimization

- Efficient database queries with proper indexing
- Lazy loading of product images
- Session caching for user data
- Minified CSS and JavaScript
- Responsive design reduces mobile data usage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Sense of Omar** - [GitHub](https://github.com/senseofomar)

## 📧 Support

For support, email support@supershopee.local or open an issue in the GitHub repository.

---

**Made with ❤️ for grocery e-commerce** | Last Updated: March 2026
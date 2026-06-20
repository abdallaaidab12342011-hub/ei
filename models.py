from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

def get_utc_now():
    """Generates a consistent naive UTC timestamp for database-neutral storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<AdminUser user='{self.username}'>"


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Numeric precision avoids rounding anomalies common with Float types
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(300), default='default.jpg')
    sku = db.Column(db.String(50), unique=True, index=True)
    weight = db.Column(db.String(50))
    dimensions = db.Column(db.String(100))
    material = db.Column(db.String(100), default='High-Quality Plastic')
    color = db.Column(db.String(100))
    
    is_featured = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product sku='{self.sku}' name='{self.name[:20]}...'>"


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50), nullable=False, index=True)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer id={self.id} name='{self.name[:20]}...'>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending', index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Cascades ensure orphaned entry records vanish alongside explicit host target purges
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order num='{self.order_number}' status='{self.status}'>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem order={self.order_id} prod={self.product_id} qty={self.quantity}>"
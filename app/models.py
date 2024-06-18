from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    country = db.Column(db.String(100))
    street = db.Column(db.String(100))
    postal_number = db.Column(db.Integer) 
    house_number = db.Column(db.Integer)   
    bus_number = db.Column(db.Integer)     
    admin_rights = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy='dynamic')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f'<Product {self.name}>'


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.id} - User: {self.user_id}, Product: {self.product_id}, Quantity: {self.quantity}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    country = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    postal_number = db.Column(db.String(20), nullable=False)
    house_number = db.Column(db.String(20), nullable=False)
    bus_number = db.Column(db.String(20))
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}, Total Price: {self.total_price}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='order_items')

    def __repr__(self):
        return f'<OrderItem {self.id} - Order: {self.order_id}, Product: {self.product_id}, Quantity: {self.quantity}>'

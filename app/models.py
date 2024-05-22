from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db,login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    country: so.Mapped[str] = so.mapped_column(sa.String(100))
    street: so.Mapped[str] = so.mapped_column(sa.String(100))
    postal_number: so.Mapped[str] = so.mapped_column(sa.String(20))
    house_number: so.Mapped[str] = so.mapped_column(sa.String(20))
    bus_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    admin_rights: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)


    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

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
    image_filename = db.Column(db.String(255))  # Voeg dit attribuut toe

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

from shop import db, app
from datetime import datetime
from shop.user.models import User
from flask import json


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(1000))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    tag = db.Column(db.String(100), nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    
    likes = db.relationship('Like', backref='product', lazy=True, cascade='all, delete-orphan')

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True), cascade='all, delete-orphan', single_parent=True)
    orders = db.relationship('Order', backref=db.backref('ordered_product', lazy=True),cascade='all, delete-orphan', single_parent=True)

    
    def count_likes(self): 
        return len(self.likes)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="Pending")
    invoice = db.Column(db.String(1000), nullable=True)  

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref='orders')
    product = db.relationship('Product', backref='ordered_in_orders')

    def generate_invoice(self):
        user = User.query.get(self.user_id)
        product = Product.query.get(self.product_id)
        self.invoice = f"""
        Order ID: {self.id}
        User: {user.username}
        Product: {product.name}
        Quantity: {self.quantity}
        Price per item: {self.price / self.quantity:.2f}
        Total Price: {self.price:.2f}
        Status: {self.status}"""
 
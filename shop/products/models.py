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
    orders = db.relationship('Order', backref=db.backref('ordered_product', lazy=True), cascade='all, delete-orphan', single_parent=True)
    ratings = db.relationship('Rating', backref='rated_product', lazy=True, cascade='all, delete-orphan')

    def count_likes(self): 
        return len(self.likes)

    def average_rating(self):
        if not self.ratings:
            return 0
        return round(sum(rating.value for rating in self.ratings) / len(self.ratings),1)
    
    def get_user_rating(self, user_id):
        rating = Rating.query.filter_by(product_id=self.id, user_id=user_id).first()
        return rating.value if rating else 0

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
    payment_status = db.Column(db.String(100), nullable=False, default="Unpaid")
    invoice = db.Column(db.String(1000), nullable=True)  

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref='orders')
    product = db.relationship('Product', backref='ordered_in_orders')


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref='user_ratings')
    product = db.relationship('Product', backref='product_ratings')


class InvoiceCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_number = db.Column(db.Integer, nullable=False, default=0)



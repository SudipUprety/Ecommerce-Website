from flask_login import UserMixin
from shop import db,app, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')
    role = db.Column(db.String(20), nullable=False, default='customer')

    likes = db.relationship('Like', backref='user', cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref=db.backref('user', lazy=True), cascade='all, delete-orphan')
    user_orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')

    def delete(self):
        for like in self.likes:
            db.session.delete(like)

        for order in self.user_orders:
            db.session.delete(order)

        for cart_item in self.cart_items:
            db.session.delete(cart_item)

        db.session.delete(self)
        db.session.commit()
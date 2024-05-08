from shop import db, app
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default.jpg')  
    tag = db.Column(db.String(100), nullable=False)
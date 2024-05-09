from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from .models import Product, Category
from flask_login import login_user, current_user, logout_user
import base64


@app.route('/add', methods=["GET","POST"])
def addproduct():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        tag = request.form['tag']
        pic = request.files['pic']
        img_data = pic.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        my_data = Product(name=name, price=price,image_file=encoded_img, tag=tag, category_id=category)
        db.session.add(my_data)
        db.session.commit()
        flash('Product added successfully')
    return render_template('products/add_product.html', categories=categories)

from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from .models import Product
from flask_login import login_user, current_user, logout_user
import base64



@app.route('/add', methods=["GET","POST"])
def addproduct():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        tag = request.form['tag']
        pic = request.files['pic']
        img_data = pic.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        my_data = Product(name=name, price=price,image_file=encoded_img, tag=tag)
        db.session.add(my_data)
        db.session.commit()
        flash('Product added successfully')
    return render_template('products/add_product.html')

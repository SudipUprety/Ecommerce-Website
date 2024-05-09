from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from shop.products.models import Category, Product
from shop.user.models import User
from flask_login import login_user, current_user, logout_user
import base64


@app.route('/admin-home')
def admin_home():
    all_products = Product.query.all()
    return render_template('admin/admin_home.html', all_products=all_products)


@app.route('/add_category', methods=["GET","POST"])
def addcategory():
    if request.method == 'POST':
        name = request.form['category']
        my_category = Category(name=name)
        db.session.add(my_category)
        db.session.commit()
        flash('Category added successfully')
    return render_template('admin/add_category.html')


@app.route('/view_category')
def viewcategory():
    all_category = Category.query.all()
    return render_template('admin/view_category.html', all_category=all_category)

@app.route('/view_user')
def viewuser():
    all_users = User.query.all()
    return render_template('admin/view_user.html', all_users=all_users)

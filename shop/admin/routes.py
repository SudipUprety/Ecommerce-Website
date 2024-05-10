from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from shop.products.models import Category, Product
from shop.user.models import User
from flask_login import login_user, current_user, logout_user
import base64


@app.route('/admin_home')
def admin_home():
    all_products = Product.query.all()
    return render_template('admin/admin_home.html', all_products=all_products)


@app.route('/view_category')
def viewcategory():
    all_category = Category.query.all()
    return render_template('admin/view_category.html', all_category=all_category)

@app.route('/view_user')
def viewuser():
    all_users = User.query.all()
    return render_template('admin/view_user.html', all_users=all_users)


@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User Deleted Successfully')
    return redirect('/view_user')




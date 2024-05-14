from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail, admin_required
from shop.products.models import Category, Product
from shop.user.models import User
from flask_login import login_user, current_user, logout_user, login_required
import base64


@app.route("/admin_login", methods=["GET","POST"])
def adminlogin():
    if request.method=='POST':
        email = request.form["email"]
        password = request.form["password"]
        user_admin = User.query.filter_by(email=email).first()
        if user_admin.role == 'admin':
            if bcrypt.check_password_hash(user_admin.password,password):
                login_user(user_admin)
                return redirect(url_for('admin_home'))
            else:
                flash('Login Unsuccessful. Please check email and password')
        else:
            flash('Your are not authorized to access admin page')
    return render_template("admin/admin_login.html")


@app.route('/admin_logout')
@admin_required
def adminlogout():
    logout_user()
    return redirect(url_for('adminlogin'))


@app.route('/admin_home')
@login_required
@admin_required
def admin_home():
    all_products = Product.query.all()
    return render_template('admin/admin_home.html', all_products=all_products)


@app.route('/view_category')
@login_required
@admin_required
def viewcategory():
    all_category = Category.query.all()
    return render_template('admin/view_category.html', all_category=all_category)

@app.route('/view_user')
@login_required
@admin_required
def viewuser():
    all_users = User.query.all()
    return render_template('admin/view_user.html', all_users=all_users)


@app.route('/delete_user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User Deleted Successfully')
    return redirect('/view_user')

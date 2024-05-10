from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from .models import Product, Category
from flask_login import login_user, current_user, logout_user
import base64


@app.route('/add_category', methods=["GET","POST"])
def addcategory():
    if request.method == 'POST':
        name = request.form['category']
        my_category = Category(name=name)
        db.session.add(my_category)
        db.session.commit()
        flash('Category added successfully')
    return render_template('products/add_category.html')


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


@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    categories = Category.query.all()
    product_to_update = Product.query.get_or_404(id)
    if request.method == 'POST':
        product_to_update.name = request.form['name']
        product_to_update.price = request.form['price']
        product_to_update.category_id = request.form['category']
        product_to_update.tag = request.form['tag']
        pic = request.files['pic']   
        img_data = pic.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        product_to_update.imgage_file = encoded_img
        db.session.commit()
        flash('Product Updated Successfully')
        return redirect('/admin_home')
    return render_template("products/update_product.html", product_to_update=product_to_update, categories=categories)


@app.route('/delete_product/<int:id>')
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    db.session.delete(product_to_delete)
    db.session.commit()
    flash('Product Deleted Successfully')
    return redirect('/admin_home')


@app.route('/update_category/<int:id>', methods=['GET', 'POST'])
def update_category(id):
    category_to_update = Category.query.get_or_404(id)
    if request.method == 'POST':
        category_to_update.name = request.form['name']
        db.session.commit()
        flash('Category updated successfully')
        return redirect('/view_category')
    return render_template("products/update_category.html", category_to_update=category_to_update)


@app.route('/delete_category/<int:id>')
def delete_category(id):
    category_to_delete = Category.query.get_or_404(id)
    db.session.delete(category_to_delete)
    db.session.commit()
    flash('Category Deleted Successfully')
    return redirect('/view_category')

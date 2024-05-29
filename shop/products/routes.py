from flask import Flask, url_for, redirect, render_template, request, flash, session, jsonify, send_from_directory,abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
import base64
from shop import app,db, admin_required
from .models import Product, Category, Rating
from shop.products.models import Like, Cart,Order
from shop.user.models import User
from fpdf import FPDF
import os
import string
from sqlalchemy import desc, func
import random



@app.route('/add_category', methods=["GET","POST"])
@login_required
@admin_required
def addcategory():
    if request.method == 'POST':
        name = request.form['category']
        my_category = Category(name=name)
        db.session.add(my_category)
        db.session.commit()
        flash('Category added successfully')
    return render_template('products/add_category.html')


@app.route('/add', methods=["GET","POST"])
@login_required
@admin_required
def addproduct():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        description = request.form['desc']
        tag = request.form['tag']
        pic = request.files['pic']
        img_data = pic.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        my_data = Product(name=name, price=price,image_file=encoded_img, description=description, tag=tag, category_id=category)
        db.session.add(my_data)
        db.session.commit()
        flash('Product added successfully')
    return render_template('products/add_product.html', categories=categories)


@app.route('/update_product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_product(id):
    categories = Category.query.all()
    product_to_update = Product.query.get_or_404(id)
    if request.method == 'POST':
        product_to_update.name = request.form['name']
        product_to_update.price = request.form['price']
        product_to_update.category_id = request.form['category']
        product_to_update.description = request.form['desc']
        product_to_update.tag = request.form['tag']
        pic = request.files['pic']   
        img_data = pic.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        product_to_update.image_file = encoded_img
        db.session.commit()
        flash('Product Updated Successfully')
        return redirect('/admin_home')
    return render_template("products/update_product.html", product_to_update=product_to_update, categories=categories)


@app.route('/delete_product/<int:id>')
@login_required
@admin_required
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    db.session.delete(product_to_delete)
    db.session.commit()
    flash('Product Deleted Successfully')
    return redirect('/admin_home')


@app.route('/update_category/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_category(id):
    category_to_update = Category.query.get_or_404(id)
    if request.method == 'POST':
        category_to_update.name = request.form['name']
        db.session.commit()
        flash('Category updated successfully')
        return redirect('/view_category')
    return render_template("products/update_category.html", category_to_update=category_to_update)


@app.route('/delete_category/<int:id>')
@login_required
@admin_required
def delete_category(id):
    category_to_delete = Category.query.get_or_404(id)
    if category_to_delete:
        products = Product.query.filter_by(category_id=id).all()
        for product in products:
            product.category_id = None  
            db.session.commit() 
    db.session.delete(category_to_delete)
    db.session.commit()
    flash('Category Deleted Successfully')
    return redirect('/view_category')


@app.route('/rate_product/<int:product_id>/<int:rating_value>', methods=['POST'])
@login_required
def rate_product(product_id, rating_value):
    product = Product.query.get_or_404(product_id)
    purchase = Order.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not purchase:
        return jsonify({'success': False, 'message': 'You can only rate products you have purchased.'}), 403

    if rating_value < 1 or rating_value > 5:
        return jsonify({'success': False, 'message': 'Invalid rating value.'}), 400

    rating = Rating.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if rating:
        rating.value = rating_value
    else:
        rating = Rating(value=rating_value, user_id=current_user.id, product_id=product_id)
        db.session.add(rating)

    db.session.commit()
    new_rating = product.average_rating()

    return jsonify({'success': True, 'new_rating': new_rating}), 200




@app.route('/single_product/<int:id>')
def single_product(id):
    product = Product.query.get_or_404(id)
    return render_template('products/single-product.html', product=product)


@app.route('/like/<int:id>', methods=['POST'])
def like(id):
    product = Product.query.get(id)
    existing_like = Like.query.filter_by(product_id=id, user_id=current_user.id).first()
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        new_like = Like(product_id=id, user_id=current_user.id)
        db.session.add(new_like)
        liked = True
    db.session.commit()
    like_count = product.count_likes()
    return jsonify({'liked': liked, 'like_count': like_count})


@app.route('/liked_post/<int:id>')
def like_user(id):
    product = Product.query.get_or_404(id)
    liked_users = []
    for like in product.likes:
        user = User.query.get(like.user_id)
        liked_users.append(user.email)
    return render_template("user/liked_user.html", product=product, liked_users=liked_users)



@app.route('/add-to-cart/<int:product_id>', methods=['POST' , 'GET'])
@login_required
def add_to_cart(product_id):
    item_to_add = Product.query.get_or_404(product_id)  
    item_exists = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_exists.product.name} has been updated', 'success')
        except Exception as e:
            db.session.rollback() 
            print('Quantity not updated:', e)
            flash(f'Quantity of {item_exists.product.name} could not be updated', 'error')
    else:
        new_cart_item = Cart()
        new_cart_item.quantity = 1
        new_cart_item.product_id = item_to_add.id
        new_cart_item.user_id = current_user.id

        try:
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f'{new_cart_item.product.name} added to cart', 'success')
        except Exception as e:
            db.session.rollback()
            print('Item not added to cart:', e)
            flash(f'{new_cart_item.product.name} could not be added to cart', 'error')

    return redirect(request.referrer)


@app.route('/view_cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.price * item.quantity
    
    return render_template('cart.html', cart=cart, amount=amount, total=amount+120)


@app.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(user_id=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    

@app.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(user_id=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    

@app.route('/removecart/<int:id>')
@login_required
def removecart(id):
    remove = Cart.query.get_or_404(id)
    db.session.delete(remove)
    db.session.commit()
    flash('Cart Deleted Successfully')
    return redirect('/view_cart')


@app.route('/place-order')
@login_required
def place_order():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    orders = []
    for item in cart_items:
        new_order = Order(
            quantity=item.quantity,
            price=float(item.product.price) * item.quantity,
            user_id=current_user.id,
            product_id=item.product.id
        )
        new_order.generate_invoice()
        db.session.add(new_order)
        orders.append(new_order)
        db.session.delete(item)  
    db.session.commit()

    pdf_filename = generate_invoice_pdf(orders)
    flash('Order placed successfully. Status is Pending.')
    return redirect(url_for('show_invoice', pdf_filename=pdf_filename))



def generate_invoice_number(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_invoice_pdf(orders):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    user = User.query.get(orders[0].user_id)
    invoice_number = generate_invoice_number()

    
    pdf.cell(200, 10, txt=f"Invoice Number: #{invoice_number}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Name: {user.username}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Email: {user.email}", ln=True)
    pdf.cell(200, 10, txt=" ", ln=True)

    
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(40, 10, txt="S.N", border=1, align="C")
    pdf.cell(60, 10, txt="Product", border=1, align="C")
    pdf.cell(20, 10, txt="Quantity", border=1, align="C")
    pdf.cell(40, 10, txt="Price per item", border=1, align="C")
    pdf.cell(40, 10, txt="Total Price", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", size=12)
    grand_total = 0
    counter = 1

    for order in orders:
        product = Product.query.get(order.product_id)
        total_price = order.price
        grand_total += total_price

        pdf.cell(40, 10, txt=f"{counter}", border=1, align="C")
        pdf.cell(60, 10, txt=f"{product.name}", border=1, align="C")
        pdf.cell(20, 10, txt=f"{order.quantity}", border=1, align="C")
        pdf.cell(40, 10, txt=f"{order.price / order.quantity:.2f}", border=1, align="C")
        pdf.cell(40, 10, txt=f"{total_price:.2f}", border=1, align="C")
        pdf.ln()

        counter += 1

    # Grand total
    pdf.cell(160, 10, txt="Grand Total", border=1, align="C")
    pdf.cell(40, 10, txt=f"{grand_total:.2f}", border=1, align="C")
    pdf.ln()

    invoice_dir = os.path.join(current_app.root_path, 'static', 'invoices')
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    pdf_filename = f'invoice_{user.id}_{invoice_number}.pdf' 
    pdf_path = os.path.join(invoice_dir, pdf_filename)
    pdf.output(pdf_path)

    return pdf_filename



@app.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(desc(Order.id)).all()
    return render_template('products/orders.html', orders=orders)


@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id == current_user.id and order.status == 'Pending':
        order.status = 'Canceled'
        db.session.commit()
        flash('Order successfully cancelled.', 'success')  
    else:
        flash('Failed to cancel order. Either the order does not exist or it is not pending.')  
    
    return redirect(url_for('order'))



@app.route('/show-invoice')
@login_required
def show_invoice():
    pdf_filename = request.args.get('pdf_filename')
    if not pdf_filename:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('show_cart'))
    return render_template('products/show_invoice.html', pdf_filename=pdf_filename)



@app.route('/invoices/<filename>')
@login_required
def serve_invoice(filename):
    try:
        return send_from_directory(os.path.join(current_app.root_path, 'static', 'invoices'), filename)
    except FileNotFoundError:
        abort(404)


@app.route('/purchased-products')
@login_required
def purchased_products():
    all_orders = Order.query.filter_by(user_id=current_user.id, status='Delivered').all()
    
    unique_products = {}
    for order in all_orders:
        if order.product_id not in unique_products:
            unique_products[order.product_id] = order
    
    unique_orders = list(unique_products.values())

    return render_template('user/purchased_products.html', orders=unique_orders)


@app.route('/filter_product', methods=['GET', 'POST'])
def filterproduct():
    categories = Category.query.all()
    filtered_products = Product.query

    if request.method == 'POST':
        category_id = request.form.get('category')
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')
        min_rating = request.form.get('min_rating')

        if category_id:
            filtered_products = filtered_products.filter(Product.category_id == category_id)
        
        if min_price:
            filtered_products = filtered_products.filter(Product.price >= float(min_price))
        if max_price:
            filtered_products = filtered_products.filter(Product.price <= float(max_price))
        
        if min_rating:
            filtered_products = filtered_products.outerjoin(Rating).group_by(Product.id).having(func.avg(Rating.value) >= float(min_rating))

    filtered_products = filtered_products.all()

    return render_template('products/filter_product.html', categories=categories, all_products=filtered_products)
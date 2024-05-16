from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from .models import User
from shop.products.models import Product, Category, Cart
from flask_login import login_user, current_user, logout_user
import random
from flask_mail import Message
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_


@app.route('/', methods=['GET', 'POST'])
def home():
    categories = Category.query.all()
    all_products = Product.query.all()
    cart=[]
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['repassword']
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:    
            if password==re_password:
                hashed_password = bcrypt.generate_password_hash(password)
                new_user = User(email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Your account is register succesfully')
                return redirect(url_for('login'))
            flash('Please enter the same password')
        flash('Email already exist.')
    return render_template('home.html', all_products=all_products, categories=categories, cart=cart)


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=='POST':
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
            
                flash('Login Unsuccessful. Please check email and password')
        else:
            flash('Register your account first')
    return render_template("user/login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=["GET","POST"])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            session['email'] = email
            otp = ''.join(random.sample('0123456789', k=4))
            session['otp'] = otp
            session['otp_timestamp'] = datetime.now(timezone.utc)
            subject = "Forgot Password - OTP Verification"
            body = f"Your OTP for password reset is: {otp}"
            msg = Message(subject, recipients=[email], body=body)
            mail.send(msg)
            return redirect(url_for('otp'))
        else:
            flash("Please register your email first!")
            return redirect('register')
    return render_template('user/forgot_password.html')


@app.route('/otp', methods=["GET", "POST"])
def otp():
    if request.method == 'POST':
        if 'otp' in session:
            user_otp = request.form["user_otp"]
            otp_timestamp = session.get('otp_timestamp')
            if datetime.now(timezone.utc) - otp_timestamp < timedelta(minutes=5):
                if user_otp == session.get('otp'):
                    return redirect(url_for('update_password'))
                else:
                    flash("OTP didn't match")
            else:
                flash("OTP expired. Please request a new one.")
                return redirect(url_for('forgotpassword'))
        else:
            flash("Please send again new OTP!")
            return redirect(url_for('forgotpassword'))
    return render_template('user/otp.html')


@app.route('/update_password', methods=["GET", "POST"])
def update_password():
    if request.method == 'POST':
        password = request.form['password']
        re_password = request.form['repassword']
        if password == re_password:
            email = session.get('email')
            user = User.query.filter_by(email=email).first()
            if user:
                hashed_password = bcrypt.generate_password_hash(password)
                user.password = hashed_password
                db.session.commit()
                session.pop('email')
                session.pop('otp')
                return redirect(url_for('login'))
            else:
                flash("No user found for this email.")
        else:
            flash("Password didn't match! Please enter the same password")
    return render_template('user/update_password.html')


@app.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        categories = Category.query.all()
        search_query = request.form['search_query']
        search_results = Product.query.filter(or_(Product.tag.like(f"%{search_query}%"), Product.name.like(f"%{search_query}%"))).all()
        return render_template('user/search_product.html', search_query=search_query, search_results=search_results,categories=categories)
    

@app.route('/sort_by_category/<int:category_id>')
def sortbycategory(category_id):
    categories = Category.query.all()
    category = Category.query.get_or_404(category_id)
    search_results = Product.query.filter_by(category_id=category_id).all()
    return render_template('user/view_by_category.html', category=category, search_results=search_results, categories=categories)

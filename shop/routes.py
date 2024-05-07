from flask import render_template, url_for, request, redirect, flash, session
from shop import app, bcrypt, db, mail
from shop.models import User
from flask_login import login_user, current_user, logout_user
import random
from flask_mail import Message
from datetime import datetime, timezone


@app.route('/', methods=['GET', 'POST'])
def home():

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
    return render_template('home.html')



@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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


@app.route('/otp')
def otp():
    return render_template('user/otp.html')

from flask import Flask, flash, redirect, url_for
from flask import request, jsonify
import requests, json
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
import os
from dotenv import load_dotenv
load_dotenv('info.env')

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER']= os.getenv('MAIL_USERNAME')


db= SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access Denied: You are not authorized to access admin page.')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


from shop.user import routes
from shop.products import routes
from shop.admin import routes



      
        


    
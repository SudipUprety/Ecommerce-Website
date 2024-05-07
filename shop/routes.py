from flask import render_template,url_for
from shop import app


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('user/login.html')

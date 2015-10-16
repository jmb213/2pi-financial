from flask import render_template
from .app import app

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')
    
@app.route('/about')
def about():
    return render_template('about.html')


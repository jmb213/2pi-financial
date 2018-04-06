from flask import render_template, url_for, redirect
from app import app, nav, db, EmailForm, EmailList


# Navigation bars
nav.Bar('nav', [
    nav.Item('Home', 'home'),
    # nav.Item('FAQ', 'faq'),
    # nav.Item('About', 'about')
])


@app.route('/', methods=['GET', 'POST'])
def home():    
    form = EmailForm()
    
    if form.validate_on_submit():                        
        dat = {'email': form.email.data}    
        email = EmailList.create(**dat)
        
        return redirect(url_for('access'))
        
    return render_template('home.html', form=form)


@app.route('/access')
def access():
    return render_template('access.html')
    
    
# @app.route('/faq')
# def faq():
    # return render_template('faq.html')


# @app.route('/about')
# def about():
    # return render_template('about.html')

    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
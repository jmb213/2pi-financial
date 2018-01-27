from flask import render_template, request, url_for, redirect, current_app, jsonify, flash, session, g, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from application import app, nav, db

from sqlalchemy import func

from .forms import LoginForm, RegistrationForm, ProfileForm

from .models import User, CustomDemoIP, Asset, AssetPosition, AccountCategory, \
    Account, UserAccount
from application import unpack_choices, form_field_choices

import re


# TODO: sort accounts
# TODO: optimize queries
# NOTE: how do we deal with negative values in the pie


# Navigation bars
nav.Bar('loggedin', [
    nav.Item('Home', 'home'),
    nav.Item('Demo', 'demo'),
    nav.Item('Profile', 'profile'),
    nav.Item('Logout', 'logout')
])

nav.Bar('loggedout', [
    nav.Item('Home', 'home'),
    nav.Item('Login', 'login'),
    nav.Item('Register', 'register')
])


#
# DATA ACCESS FUNCTIONS
#

def query_result_to_dict(q_result):
    """
    Take the result of a query through SqlAlchemy
    and convert it into a dictionary
    """
    return [dict(zip(row.keys(), row)) for row in q_result]


# USER ACCESS

def get_user_by_id(user_id):
    return User.get(user_id)


def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

 
def get_user_accounts(user):
    return UserAccount.query.filter(UserAccount.user_id == user.id).all()
    
    
def get_demo_users():
    """
    Get all of the demo accounts (filtering out custom demo accounts if wanted)
    """
    return User.query.filter(User.is_demo == True).all()
    
    
# USER POSITIONS

def get_user_asset_class_summary(user):
    """
    Given a user, return a summary of his positions summarised
    across Asset Class
    @return: two columns (AssetClass, value)
    """
    app.logger.info("Getting asset class summary for: %s -- %s" %(user.email, str(user.id)))

    out = db.session.query(
        Asset.asset_class.label('asset_class'),
        func.sum(AssetPosition.value).label('value')). \
    join(AssetPosition). \
    join(UserAccount). \
    group_by(Asset.asset_class). \
    filter(UserAccount.user_id == user.id). \
    all()

    return out


def get_user_account_summary(user):
    """
    Given a user, return a summary of his positions summarised
    by User Account with other meta information
    @return: 6 columns (id, account_id, account_name, accountegory_id,
                                       account_category_name, value)
    """
    app.logger.info("Getting user account summary for: %s -- %s" %(user.email, str(user.id)))

    out = db.session.query(
            UserAccount.id.label('id'),
            Account.id.label('account_id'),
            Account.account_name.label('account_name'),
            AccountCategory.id.label('account_category_id'),
            AccountCategory.account_category_name.label('account_category_name'),
            func.sum(AssetPosition.value).label('value')). \
        join(AssetPosition). \
        join(Account). \
        join(AccountCategory). \
        group_by(UserAccount, Account, AccountCategory). \
        filter(UserAccount.user_id == user.id). \
        all()

    return out


def get_user_positions(user):
    """
    Given a user, return each of his positions
    @return: AssetPosition, Asset, account_id, user_id
    """
    app.logger.info("Getting positions for: %s -- %s" %(user.email, str(user.id)))

    out = db.session.query(
            AssetPosition,
            Asset,
            UserAccount.account_id,
            UserAccount.user_id). \
        join(Asset). \
        join(UserAccount). \
        filter(UserAccount.user_id == user.id). \
        all()
    # app.logger.info(out[0].keys())
    return out


# MANIPULATING DATA INTO DIGESTIBLE FORMS

def configure_account_category_output(user_account_summary):
    """
    Take the user account summary and output a data structure that will be
    used by the HTML template for displaying account values
    """
    # TODO: order the accounts better

    # Get the unique account categories
    account_cats = list(set([a_summary.account_category_id for a_summary in user_account_summary]))

    account_categories = []
    for acct_cat_id in account_cats:

        # Get the category name
        acct_cat_name = None
        for a_summary in user_account_summary:
            if a_summary.account_category_id == acct_cat_id:
                acct_cat_name = a_summary.account_category_name
                break

        # Get all of accounts that are associated with the account category
        sub_accounts = [(a_summary.account_id, a_summary.account_name, a_summary.value)
                                for a_summary in user_account_summary
                                if a_summary.account_category_id == acct_cat_id]

        # JSON for the accounts
        out_account_list = [{
                'label': acct[1],
                'id': 'input_%d_%d' %(acct_cat_id, acct[0]),
                'value':  int(acct[2])
            } for acct in sub_accounts]

        # JSON for the account category
        account_category = {
            'heading': acct_cat_name,
            'heading_id': 'account_cat_head_%d' %acct_cat_id,
            'id': 'account_cat_%d' %acct_cat_id,
            'account_sum': int(sum([a.get('value') for a in out_account_list])),
            'accounts': out_account_list
        }
        account_categories.append(account_category)

    return account_categories


def calculate_user_networth(user_account_summary):
    """
    Given a user accounts' summary, calculate his networth by simply adding
    the accounts' value together
    """
    networth = 0
    for act in user_account_summary:
        networth += act.value

    return int(networth)


#
# VIEWS
#

@app.before_request
def before_request():
    """
    Set the global enviornment class' user to the current user
    """
    g.user = current_user


@app.route('/')
def home():
    """
    Home page -
    """
    return render_template('home.html')


@app.route('/chart_data.json')
def chart_data():
    """
    Output the data required to make the charts as JSON
    """
    asset_class_summary = get_user_asset_class_summary(current_user)
    asset_class_summary = query_result_to_dict(asset_class_summary)

    return jsonify(asset_class_summary = asset_class_summary)


@app.route('/demo', methods = ['GET', 'POST'])
@login_required
def demo():
    """
    Render the demo page, which takes both GET and POST requests
    GET requests should return the current user's profile
    POST requests evaluate the data from the post and output the corresponding user
    """
    # app.logger.info('demo')

    if request.method == 'POST':
        # Load in the data in the POST request's form
        form_dict = request.form

        # app.logger.info('Select field changed: %s' % request.form['select-changed'])
        # If the default select list has been changed
        # if form_dict.get('select-changed') == 'yes':
            # form_user_id = form_dict.get('select-cohort')
            # Get the user by its ID in the database
            # user = get_user_by_id(form_user_id)
        # else:
            # Get the user's IP address for logging and create a new demo account
            # ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            # user = make_custom_demo_user(form_dict, ip_addr)

    # Get the account assets for the user for the side bar inputs
    user_accounts = get_user_account_summary(current_user)

    # Add up the net worth from the users account
    net_worth = calculate_user_networth(user_accounts)

    # Transform the user account summary into digestible fields
    account_categories = configure_account_category_output(user_accounts)

    # Get the default demo accounts for the select list
    demo_users =  get_demo_users()

    # Example suggestions
    suggestions = [
        {'account': 'broker A', 'asset': 'SPY', 'asset_position': 2000, 'suggestion': 'buy $2000'},
        {'account': 'broker B', 'asset': 'EEM', 'asset_position': 1000, 'suggestion': 'sell $1000'},
        {'account': 'bank A', 'asset': 'checking', 'asset_position': 10000, 'suggestion': 'transfer $1000 to broker A'}
    ]

    kwargs = {
        'account_categories': account_categories,
        'user_name': current_user.user_name, 
        'net_worth': net_worth,
        'suggestions': suggestions
    }

    return render_template('demo.html', **kwargs)


    
def copy_users_accounts_and_positions(copy_user, new_user):
    copy_user_accounts = get_user_accounts(copy_user)
    
    app.logger.info(copy_user_accounts)
    
    user_accounts = []
    
    for copy_user_account in copy_user_accounts:
        account_id = copy_user_account.account_id
        account = copy_user_account.account
        user_id = new_user.id
        
        positions = []
        for position in copy_user_account.positions:
            asset_id = position.asset_id
            asset = position.asset
            value = position.value
            
            positions.append(AssetPosition.create(asset_id = asset_id, asset = asset, value = value))            
        
        user_account = UserAccount.create(account_id = account_id, account = account, 
            user_id = user_id, positions = positions)
            
        user_accounts.append(user_account)
    
    new_user.update(user_accounts = user_accounts)


    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Default registration view
    """
    # If a user is already logged in    
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
    
    demo_users = get_demo_users()
    
    form = RegistrationForm()
    form.base_profile.choices = unpack_choices([user.user_name for user in demo_users])
    
    if form.validate_on_submit():
                
        base_profile = form.base_profile.data
        
        dat = {'email': form.email.data,
                  'user_name': form.email.data,
                  'password': form.password.data,
                  'base_profile': base_profile}
    
        user = User.create(**dat)
        
        demo_users = get_demo_users()
        demo_user = demo_users[base_profile]
        
        copy_users_accounts_and_positions(demo_user, user)
        
        login_user(user)
        
        return redirect(url_for('profile'))
        
    return render_template('register.html', form=form)
    
    
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Default registration view
    """
    form = ProfileForm(obj = current_user)
    
    form.gender_id.choices = unpack_choices(form_field_choices.get('gender'))
    form.education_id.choices = unpack_choices(form_field_choices.get('education'))
    form.financial_advisor_id.choices = unpack_choices(form_field_choices.get('financial_advisor'))
    form.occupation_id.choices = unpack_choices(form_field_choices.get('occupation'))
    form.experience_id.choices = unpack_choices(form_field_choices.get('experience'))
            
    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.save()
        
        return redirect(url_for('profile'))
        
    return render_template('profile.html', form=form)
    
  
@app.route('/login',methods=['GET', 'POST'])
def login():
    """
    Default login view
    """
    # If a user is already logged in
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))

    # Load in the WTF form
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data

        login_user(form.user, remember=form.remember_me.data)

        # flash('Login successful for email="%s"' % form.email.data)

        next = request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        # if not next_is_valid(next):
            # return flask.abort(400)
        
        return redirect(next or url_for('home'))

    return render_template('login.html',  form=form) 
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.route('/contact')
# def about():
    # return render_template('contact_us.html')


# @app.route('/faq')
# def about():
    # return render_template('faq.html')


# @app.route('/about')
# def about():
    # return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


#
# Data pipeline
#

@app.route('/recommendations')
def recommendations():
    """
    Template for the recommendations tab
    """

    suggestions = [
        {'account': 'broker A', 'asset': 'SPY', 'asset_position': 2000, 'suggestion': 'buy $2000'},
        {'account': 'broker B', 'asset': 'EEM', 'asset_position': 1000, 'suggestion': 'sell $1000'},
        {'account': 'bank A', 'asset': 'checking', 'asset_position': 10000, 'suggestion': 'transfer $1000 to broker A'}
    ]

    kwargs = {
        'suggestions': suggestions
    }

    return render_template('recommendations.html', **kwargs)


@app.route('/risk_test', methods = ['GET', 'POST'])
def risk_test():
    """
    Template for the risk test questions tab
    """

    # TODO: move these to some config file
    possible_annuity_levels = range(60000, 160000, 20000)

    question_prompts = [
        "I'd be very unhappy if I had",
        "I'd be unhappy if I had",
        "I'd be content if I had",
        "I'd be satisfied if I had",
        "I'd be very happy if I had"
    ]
    
    num_questions = len(question_prompts)
    
    if request.method == 'POST':
        # Load in the data in the POST request's form
        form_dict = request.form
        
        level_answers = []
        for question_id in range(num_questions):
            level_answers.append(form_dict.get('risk-question-%d' %question_id))

        return str(level_answers)
        
        # user_annuity_levels = {}
        # for level_answer in level_answers:

        # Get the user ID
        # Get the user's IP address for logging and create a new demo account
        # ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        # user = make_custom_demo_user(form_dict, ip_addr)

        # return redirect(url_for('recommendations'))

    elif request.method == 'GET':

        kwargs = {
            'possible_annuity_levels': possible_annuity_levels,
            'question_prompts': question_prompts
        }

        return render_template('risk_test.html', **kwargs)

    else:
        abort(404)

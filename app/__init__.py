from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.navigation import Navigation
from flask_analytics import Analytics
import os
import logging

# Configure our app and database from the file
app = Flask(__name__)
app.config.update(
    ENV = os.environ.get('ENV'),
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL'),
    SECRET_KEY = os.environ.get('SECRET_KEY'),
    WTF_CSRF_ENABLED = True
)

Analytics(app)
app.config['ANALYTICS']['GOOGLE_UNIVERSAL_ANALYTICS']['ACCOUNT'] = ''

# Set up logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('Enviornment: %s' %app.config['ENV'])

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename = filename)
)

# Analytics

# setup assets
assets = Environment(app)
assets.url_expire = False
assets.debug = app.config['ENV'] == 'development'
assets.load_path = ['%s/static' % app.config.root_path]

assets.register('css',
    Bundle(
      'css/vendor/*.css',
      'css/*.css',
      output='css/app.%(version)s.css'))

# Bundle these in a specific order for dependency reasons
assets.register('js', Bundle(
    'js/vendor/jquery/jquery.js',
    'js/vendor/d3/d3.min.js',
    'js/vendor/nvd3/nv.d3.min.js',
    'js/vendor/*.js',
    'js/*.js',
    output='js/app.%(version)s.js'))
    
# For the navigation bar
nav = Navigation(app)
    
# Create databases
db = SQLAlchemy(app)
app.logger.info('SQL Alchemy loaded')

class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_or_404(cls, id):
        return cls.query.get_or_404(id)

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

        
class EmailList(db.Model, CRUDMixin):
    __tablename__ = 'email'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True)
        
    def __repr__(self):
        return '<EmailList %r>' % (self.email)

        
db.create_all()
app.logger.info('Data tables created')


# Forms
from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email, ValidationError

class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_email(form, field):
        email = EmailList.query.filter(EmailList.email == field.data).first()
        if email is not None:
            raise ValidationError("A user with that email already exists")

            
# Load everything else
from app import views

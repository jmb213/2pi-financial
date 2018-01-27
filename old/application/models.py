from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from application import db

# TODO: comments
# TODO: lazy load? optimize?

    
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

    # We will also proxy Flask-SqlAlchemy's get_or_404
    # for symmetry
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

    
class AssetPosition(db.Model, CRUDMixin):
    __tablename__ = 'asset_positions'
    
    id = db.Column(db.Integer, primary_key = True)
    
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    asset = db.relationship('Asset') # Many asset positions are linked to an asset
       
    user_account_id = db.Column(db.Integer, db.ForeignKey('user_account.id'))
    
    value = db.Column(db.Float)
    
    def __repr__(self):
        return '<Asset Position %s: %d>' % (self.asset.asset_name, int(self.value))
                
class Asset(db.Model, CRUDMixin):
    __tablename__ = 'asset'
    
    id = db.Column(db.Integer, primary_key = True)
    asset_name = db.Column(db.String(32))
    asset_class = db.Column(db.String(32))
    is_demo = db.Column(db.Boolean, default = False)
    
    def __repr__(self):
        return '<Asset %s / %s>' % (self.asset_name, self.asset_class)
        
class CustomDemoIP(db.Model, CRUDMixin):
    """
    This table is for simply counting up the custom demo ids
    """
    __tablename__ = 'custom_demo_ip'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(32))
    
    def __repr__(self):
        return '<CustomDemoIP %d -- %s>' % (self.id, self.ip_address)
                          
class UserAccount(db.Model, CRUDMixin):
    __tablename__ = 'user_account'
    
    id = db.Column(db.Integer, primary_key = True)
    
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship('Account')    
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    
    # One to many mapping that is bidirectional (user has many positions / positions mapped to one user)
    positions = db.relationship('AssetPosition', backref='account', lazy='dynamic')
    
    def __repr__(self):
        return '<UserAccount %d -- %s>' % (self.user_id, self.account_id)
        
class Account(db.Model, CRUDMixin):
    __tablename__ = 'account'
    
    id = db.Column(db.Integer, primary_key = True)
    account_name = db.Column(db.String(255))
    
    is_taxable = db.Column(db.Boolean, default = True)
    
    account_category_id = db.Column(db.Integer, db.ForeignKey('account_category.id'))
    account_category = db.relationship('AccountCategory')
    
    def __repr__(self):
        return '<Account %s>' % (self.account_name)
                    
class AccountCategory(db.Model, CRUDMixin):
    __tablename__ = 'account_category'
    
    id = db.Column(db.Integer, primary_key = True)
    account_category_name = db.Column(db.String(255), unique=True)
    
    def __repr__(self):
        return '<AccountCategory %s>' % (self.account_category_name)
        
        
class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    pw_hash = db.Column(db.String(255))
    user_name = db.Column(db.String(255))
    
    birthdate =db.Column(db.Date)
    salary = db.Column(db.Integer)    
    
    gender_id = db.Column(db.Integer)
    occupation_id = db.Column(db.Integer)
    experience_id = db.Column(db.Integer)
    education_id = db.Column(db.Integer)
    financial_advisor_id = db.Column(db.Integer)
    base_profile = db.Column(db.Integer)
    
    is_demo = db.Column(db.Boolean, default=False)
    
    # One to many mapping that is bidirectional (user has many positions / positions mapped to one user)
    user_accounts = db.relationship('UserAccount', backref='user', lazy='dynamic') 
    
    
    @property
    def is_active(self):
        """All users are active except demo"""
        return not self.is_demo
        
    @property
    def is_authenticated(self):
        """All users are active except demo"""
        return not self.is_demo

    @property
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
        
    @hybrid_property
    def password(self):
        return self.pw_hash

    @password.setter
    def password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def __repr__(self):
        return '<User %r>' % (self.user_name)
        
        
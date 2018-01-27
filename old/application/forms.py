from flask.ext.wtf import Form
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import StringField, PasswordField, BooleanField, DateField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, ValidationError, Optional

from .models import User

# TODO: CSRF

                                      
class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me", default=False)
    
    # WTForms supports "inline" validators
    # which are methods of our `Form` subclass
    # with names in the form `validate_[fieldname]`.
    # This validator will run after all the
    # other validators have passed.
    def validate_password(form, field):
        try:
            user = User.query.filter(User.email == form.email.data).one()
        except (MultipleResultsFound, NoResultFound):
            raise ValidationError("Invalid user")
        if user is None:
            raise ValidationError("Invalid user")
        if not user.check_password(form.password.data):
            raise ValidationError("Invalid password")
            
        # Make the current user available to calling code.
        form.user = user
   
   
class ProfileForm(Form):
    user_name = StringField("User Name")
    birthdate = DateField("Birthdate", format='%Y-%m-%d')
    gender_id = SelectField("Gender", coerce = int)
    education_id = SelectField("Education", coerce = int)
    financial_advisor_id = SelectField("Financial advisor?", coerce = int)
    occupation_id = SelectField("Occupation", coerce = int)
    experience_id = SelectField("Work experience", coerce = int)
    salary = IntegerField("Salary", validators=[Optional()])


class RegistrationForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    base_profile = SelectField("Base profile", coerce = int, default = 0)

    def validate_email(form, field):
        user = User.query.filter(User.email == field.data).first()
        if user is not None:
            raise ValidationError("A user with that email already exists")
            
    def confirm_password(form):
        if password.data != confirm_password.data:
            raise ValidationError("Passwords do not match")

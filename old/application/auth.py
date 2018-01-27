from flask.ext.login import LoginManager

from models import User

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """
    Method required by Flask-Login
    """
    return User.query.get(user_id)

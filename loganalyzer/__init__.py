from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from .config import config_by_name

db=SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

#debug bar
toolbar = DebugToolbarExtension()

#for dislaying of time
moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .supportbundles import supportbundles as supportbundles_blueprint
    app.register_blueprint(supportbundles_blueprint, url_prefix='/supportbundles')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    return app
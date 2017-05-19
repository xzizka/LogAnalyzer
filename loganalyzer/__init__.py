import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment

app = Flask(__name__)
app.config['SECRET_KEY']='jqleSv89245tl#=4gm;45gP54*/76542@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pypostgresql://xzizka:Passw0rd@10.11.78.140:5432/loganalyzer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.init_app(app)

moment = Moment(app)

import loganalyzer.models
import loganalyzer.views

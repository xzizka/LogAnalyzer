from flask import Blueprint

supportbundles = Blueprint('supportbundles', __name__)

from . import views
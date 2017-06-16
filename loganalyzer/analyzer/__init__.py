from flask import Blueprint

analyzer = Blueprint('analyzer', __name__)

from . import views
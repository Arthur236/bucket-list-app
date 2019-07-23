from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
bucket_lists_blueprint = Blueprint('bucket_lists', __name__)

from . import views

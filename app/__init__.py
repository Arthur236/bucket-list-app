from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_scss import Scss

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    Scss(app)
    db.init_app(app)

    @app.route("/", methods=['GET'])
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def dummy_error_404(_error):
        """
        Handles 404 errors
        """
        message = {
            'status': 404,
            'message': 'The resource at {}, cannot be found.'
        }

        return render_template('index.html')

    @app.errorhandler(500)
    def dummy_error_500(_error):
        """
        Handles 500 errors
        """
        message = {
            'status': 500,
            'message': 'Looks like something went wrong. '
                       'Our team of experts is working to fix this.'
        }

        return render_template('index.html')

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    from .bucket_lists import bucket_lists_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(bucket_lists_blueprint)

    return app

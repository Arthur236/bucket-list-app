import re

from flask.views import MethodView
from flask import flash, redirect, request, session, url_for

from . import auth_blueprint
from app.models import User
from ..decorators import MyDecorator
my_dec = MyDecorator()


class RegistrationView(MethodView):
    """
    This class registers a new user.
    """
    @staticmethod
    def post():
        """
        Handle POST request for this view. Url ---> /auth/register
        """
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']

        if email and password and username and cpassword:
            email_resp = my_dec.validate_email(email)

            if not email_resp:
                flash("The email provided is not valid.")
                return redirect(url_for('index'))

            if not re.match("^[a-zA-Z0-9 _]*$", username):
                flash("The username cannot contain special characters. Only underscores")
                return redirect(url_for('index'))

            if (username.length < 3 or username.length > 50):
                flash('Username should be between 3 and 50 characters')
                return redirect(url_for('index'))

            if len(password) < 6:
                flash("The password should be at least 6 characters long")
                return redirect(url_for('index'))

            if password != cpassword:
                flash("The passwords do not match")
                return redirect(url_for('index'))

            user = User.query.filter_by(email=request.form['email']).first()

            if not user:
                # There is no user so we'll try to register them
                try:
                    user = User(username=username, email=email, password=password)
                    user.save()

                    session['username'] = username

                    flash("You were automatically logged in.")
                    return redirect(url_for('bucketlists'))
                except Exception as e:
                    # An error occured, therefore return a string message containing the error
                    flash(str(e))
                    return redirect(url_for('index'))
            else:
                # There is an existing user. We don't want to register users twice
                # Return a message to the user telling them that they they already exist
                flash('User already exists. Please login.')
                return redirect(url_for('index'))


class LoginView(MethodView):
    """
    This class-based view handles user login and access token generation.
    """
    @staticmethod
    def post():
        """
        Handle POST request for this view. Url ---> /auth/login
        """
        email = str(request.form.get('email', ''))
        password = str(request.form.get('password', ''))

        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=email).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(password):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                if access_token:
                    return redirect(url_for('bucketlists'))
            else:
                # User does not exist. Therefore, we return an error message
                flash('The user does not exist or the password is invalid, Please try again.')
                return redirect(url_for('index'))

        except Exception as e:
            # Create a response containing an string error message
            flash(str(e))
            return redirect(url_for('index'))


# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')


# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url --->  /auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)

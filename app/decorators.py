"""
Custom decorator functions
"""
import re
import jwt
from flask import flash, redirect, session, url_for

from app.models import User


class MyDecorator(object):
    """
    Class to hold decorator methods
    """
    @staticmethod
    def validate_email(email):
        """
        Helper function to validate email
        """
        email_exp = r"(^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$)"

        if re.match(email_exp, email):
            return True

        return False

    @staticmethod
    def is_authenticated():
        """
        Checks if a user is logged in
        """
        if "username" not in session:
            return {
              'status': False
            }

        # Query for the user and return their user_id
        username = session['username']

        try:
            user = User.query.filter_by(username=username).first()
            return {
              'status': True,
              'user_id': user.id
            }
        except Exception as e:
            return {
              'status': False,
              'user_id': None
            }

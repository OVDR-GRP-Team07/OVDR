"""
Form Validation for User Authentication
Author: Zixin Ding

This module defines WTForms-based validation classes used for:
- User Registration
- User Login

It ensures input correctness (length, matching password fields),
and checks for unique usernames by querying the database.

Used by: routes/auth.py
"""

import wtforms
from wtforms.validators import Length, EqualTo
from models import User
# -------------------------------
# Form Classes for Input Validation
# -------------------------------

# RegisterForm:
#   Used to validate registration form input from the frontend.
#   Fields:
#       - username: must be unique, 3-20 characters
#       - password: must be 6-20 characters
#       - password_confirm: must match password
# Form: mainly used to verify whether the submitted data of the front-end meets the requirements
class RegisterForm(wtforms.Form):
    username = wtforms.StringField(validators=[Length(min=3, max=20, message="The username must be 3~20 characters long!")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="The password must be 6~20 characters long!")])
    password_confirm = wtforms.StringField(validators=[EqualTo("password")])
    
    # The user name must be unique
    def validate_username(self,field):
        """
        Custom validator: ensure username is not already taken.

        Args:
            field: the form field containing the username value

        Raises:
            ValidationError: if username already exists in DB
        """
        username = field.data
        user = User.query.filter_by(username=username).first()
        if user:
            raise wtforms.ValidationError(message="This username is already taken. Please choose another one.")

    # To be expanded: email registeration


# LoginForm:
#   Used to validate login credentials.
#   Fields:
#       - username: must be 3-20 characters
#       - password: must be 6-20 characters
class LoginForm(wtforms.Form):
    username = wtforms.StringField(validators=[Length(min=3, max=20, message="Wrong username.")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="Wrong password.")])
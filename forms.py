from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length


class CSRFProtection(FlaskForm):
    """CSRFProtection form, intentionally left blank."""


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserForm(FlaskForm):
    """Form for adding and logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class AddLocationForm(FlaskForm):
    """Form for adding a location."""

    owner = StringField('Owner', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[
                            DataRequired(), Length(min=6)])

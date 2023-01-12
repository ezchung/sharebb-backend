from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, FileField
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

# TODO: add properties when working with locations and connecting. Maybe delete FIXME:
class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class AddLocationForm(FlaskForm):
    """Form for adding a location."""

    price = FloatField('Price', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[
                            DataRequired(), Length(min=6)])
    image_url = FileField('Image URL', validators=[DataRequired()])



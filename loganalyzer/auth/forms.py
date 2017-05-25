from flask_wtf import FlaskForm
from ..models import User
from wtforms.fields import PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')

#Just for future use
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3,80), Regexp('^[A-Za-z0-9_]{3,}$', message='Numbers, letters, underscores.')])
    password = PasswordField('Password',validators=[DataRequired(), EqualTo('password2',message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(), Length(1,120), Email()])

    def validate_email(self,email_field):
        if User.query.filter_by(email=email_field.data).first():
                raise ValidationError('This email already exists')

    def validate_username(self, username_field):
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('This username already exists')


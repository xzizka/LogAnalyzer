from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from flask import request
from wtforms.fields import IntegerField, TextAreaField, FileField, PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Regexp, EqualTo, Email, ValidationError

from loganalyzer.models import User


class SBForm_base(FlaskForm):
    service_request=IntegerField('Service Request number', validators=[DataRequired(message='You must input a valid number'),NumberRange(min=0,message='Input is not a valid number.')])
    comment=TextAreaField('Add comments',validators=[Optional()])
    tags = StringField('Tags', validators=[Regexp(r'^[a-z,A-Z0-9, ]*$',
                                                  message='Tags can only contains letters and numbers')])

    def validate(self):

        #if not self.input_file and request.endpoint == "edit":
        #    self.input_file.data = FileField()

        if not FlaskForm.validate(self):
            return False

        stripped = [t.strip() for t in self.tags.data.split(',')]
        not_empty = [tag for tag in stripped if tag]
        tagset = set(not_empty)
        self.tags.data = ",".join(tagset)

        return True


class SBForm_upload(SBForm_base):
    input_file=FileField('Select Support Bundle',validators=[FileRequired(message='The Support Bundle is mandatory')])


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

    def validate_email(self, username_field):
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('This username already exists')


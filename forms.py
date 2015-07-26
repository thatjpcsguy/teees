#/usr/bin/env python2.7

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import Required, Length, Regexp

# RegEx declaration
username_regex = '^\w{3,32}$'
password_regex = '^.{6,255}$'


class LoginForm(Form):
    username = StringField('username', validators=[Required(), Length(max=32), Regexp(username_regex)])
    password = PasswordField('password', validators=[Required(), Length(max=255), Regexp(password_regex)])


class RegistrationForm(Form):
    username = StringField('username', validators=[Required(), Length(max=32), Regexp(username_regex)])
    password = PasswordField('password', validators=[Required(), Length(max=255), Regexp(password_regex)])
    email = StringField('email', validators=[Required(), Length(max=255)])

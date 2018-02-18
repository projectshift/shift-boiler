from shiftschema.ext.flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf import RecaptchaField as RecaptchaField

"""
User forms
This is a collection of forms for the user functionality. They are being
used by pluggable user views in kernel so you are good to go from the start,
although you are free to extend these or use your own if you so desire.
"""


class LoginForm(Form):
    email = StringField('email')
    password = PasswordField('password')
    remember = BooleanField('remember')
    recaptcha = None
    def __init__(self, *args, captcha=False, **kwargs):
        super().__init__(*args, **kwargs)


class RegisterForm(Form):
    recaptcha = RecaptchaField()
    email = StringField('email')

    password = PasswordField('password', validators=[
        DataRequired(),
        EqualTo('confirm', 'Password must match confirmation')
    ])
    confirm = PasswordField('confirm', validators=[
        DataRequired(),
        EqualTo('password', 'Password must match confirmation')
    ])


class ResendEmailConfirmationForm(Form):
    """ Allows user to resend confirmation email """
    recaptcha = RecaptchaField()
    email = StringField('email', validators=[
        DataRequired(),
    ])


class FinalizeSocial(Form):
    email = StringField('email', validators=[])


class ChangeEmailForm(Form):

    email = StringField('email', validators=[
        DataRequired(),
        EqualTo('confirm_email', 'Email must match confirmation')
    ])
    confirm_email = StringField('email', validators=[
        DataRequired(),
        EqualTo('confirm_email', 'Email must match confirmation')
    ])


class ChangePasswordForm(Form):

    password = PasswordField('password', validators=[
        DataRequired(),
        EqualTo('confirm_password', 'Password must match confirmation')
    ])
    confirm_password = PasswordField('confirm', validators=[
        DataRequired(),
        EqualTo('password', 'Password must match confirmation')
    ])


class RecoverPasswordRequestForm(Form):
    recaptcha = RecaptchaField()
    email = StringField('email', validators=[
        DataRequired(),
    ])


class RecoverPasswordForm(Form):
    password = PasswordField('password', validators=[
        DataRequired(),
        EqualTo('confirm_password', 'Password must match confirmation')
    ])
    confirm_password = PasswordField('confirm', validators=[
        DataRequired(),
        EqualTo('password', 'Password must match confirmation')
    ])


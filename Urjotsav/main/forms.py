from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from Urjotsav.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    enrollment_number = StringField('Enrollment Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    dept_name = StringField('Department Name', [DataRequired()])
    branch = StringField('Branch', [DataRequired()])
    submit = SubmitField('Register')

    def validate_enrollment_number(self, enrollment_number):
        user = User.query.filter_by(enrollment_number=enrollment_number.data).first()
        if user:
            raise ValidationError(
                'The Enrollment Number has already been registered!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The email has already been registered!')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

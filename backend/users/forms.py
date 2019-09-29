from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, ValidationError


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=
                             [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=
                                     [DataRequired()])
    submit = SubmitField('Sign Up')

    @staticmethod
    def validate_password(self, password):
        if len(password.data) < 8:
            flash("Password must be at least eight characters long.", 'danger')
            raise ValidationError("Password must be at least eight characters long.")

    @staticmethod
    def validate_confirm_password(self, password):
        if self.password.data != self.confirm_password.data:
            flash("The passwords do not match.", 'danger')
            raise ValidationError("The passwords do not match.")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

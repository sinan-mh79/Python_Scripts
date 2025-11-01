from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re


# Custom Password Validator
def strong_password(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long.")
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError("Password must contain at least one alphabetic letter.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&* etc).")


# Register Form 
class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=25, message="Username must be 3–25 characters."),
        ],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(message="Enter a valid email address.")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            strong_password,
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")


#  Login Form 
class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(message="Enter a valid email address.")]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Forgot Password Form 
class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(message="Enter a valid email address.")]
    )
    submit = SubmitField("Send Reset Link")


#  Reset Password Form 
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            strong_password,
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Reset Password")

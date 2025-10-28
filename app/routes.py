from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_limiter.errors import RateLimitExceeded
from datetime import datetime
from functools import wraps
import re, secrets

from . import db, limiter
from .models import User
from .email_utils import send_email
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

main = Blueprint("main", __name__)



# Rate Limit Handler
@main.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    flash("Too many requests! Please wait a moment.", "error")
    return redirect(url_for("main.home"))


# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated_function


# Home Page

@main.route("/")
def home():
    return render_template("home.html")



# Register

@main.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data

        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists", "error")
            return redirect(url_for("main.register"))

        
        if len(password) < 8 or not re.search(r"\d", password) \
           or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) \
           or not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", password):
            flash("Weak password! Include upper, lower, number, and special character.", "error")
            return redirect(url_for("main.register"))

        token = secrets.token_urlsafe(16)
        user = User(username=username, email=email, verification_token=token)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        link = url_for("main.verify_email", token=token, _external=True)
        try:
            send_email(email, "Verify your email", f"Click here to verify your account:\n{link}")
            flash("Registration successful! Please check your email for verification link.", "success")
        except Exception as e:
            print(f"Email error: {e}")
            flash("Email could not be sent. Check console for verification link.", "warning")
            print(f"Verification link: {link}")

        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)

# Email Verification

@main.route("/verify/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash("Invalid or expired verification link!", "error")
        return redirect(url_for("main.home"))

    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    flash("Email verified successfully! You can now login.", "success")
    return redirect(url_for("main.login"))



# Login

@main.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("main.login"))

        
        if not user.is_verified:
            token = secrets.token_urlsafe(16)
            user.verification_token = token
            db.session.commit()
            link = url_for("main.verify_email", token=token, _external=True)
            try:
                send_email(user.email, "Verify your email", f"Click to verify:\n{link}")
                flash("Please verify your email. New verification link sent.", "warning")
            except Exception as e:
                print(f"Email sending error: {e}")
                flash("Please verify your email. Check console for link.", "warning")
                print(f"Verification link: {link}")
            return redirect(url_for("main.login"))

        # Login user
        session["user_id"] = user.id
        session["username"] = user.username
        flash(f"Welcome {user.username}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)



# Dashboard 

@main.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)


# Logout

@main.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.home"))


# Forgot Password
@main.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No user found with this email.", "error")
            return redirect(url_for("main.forgot_password"))

        token = secrets.token_urlsafe(16)
        user.reset_token = token
        user.token_sent = datetime.utcnow()
        db.session.commit()

        link = url_for("main.reset_password", token=token, _external=True)
        try:
            send_email(email, "Reset your password", f"Click here to reset your password:\n{link}")
            flash("Password reset link sent! Check your email.", "success")
        except Exception as e:
            print(f"Email sending error: {e}")
            flash("Password reset link could not be sent. Check console.", "warning")
            print(f"Reset link: {link}")

        return redirect(url_for("main.login"))

    return render_template("forgot_password.html", form=form)


# Reset Password

@main.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("main.home"))

    
    if user.token_sent and (datetime.utcnow() - user.token_sent).total_seconds() > 900:
        flash("Reset link expired. Please try again.", "error")
        return redirect(url_for("main.forgot_password"))

    if form.validate_on_submit():
        password = form.password.data

        user.set_password(password)
        user.reset_token = None
        user.token_sent = None
        db.session.commit()

        flash("Password reset successful! You can now login.", "success")
        return redirect(url_for("main.login"))

    return render_template("reset_password.html", form=form, token=token)



# Prevent Browser Cache 
@main.after_request
def add_header(response):
    """Ensure sensitive pages aren't cached by browser."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

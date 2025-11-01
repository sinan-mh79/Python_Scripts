from flask import Blueprint, render_template, redirect, url_for, flash, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .email_utils import send_email
import os

main = Blueprint("main", __name__)
s = URLSafeTimedSerializer(os.getenv("FLASK_SECRET_KEY", "dev_secret"))


@main.route("/")
def home():
    return render_template("home.html", title="Home")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("main.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = s.dumps(email, salt="email-confirm")
        link = url_for("main.verify_email", token=token, _external=True)
        send_email(email, "Verify Your Email", f"Click here to verify your email:\n{link}")

        flash("Verification email sent! Please check your inbox.", "info")
        return render_template("blank.html", title="Verify Email")

    return render_template("register.html", form=form, title="Register")


@main.route("/verify_email/<token>")
def verify_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
    except (SignatureExpired, BadSignature):
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for("main.register"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("main.register"))

    user.is_verified = True
    db.session.commit()
    return render_template("verify_success.html", title="Email Verified")


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("main.login"))

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("main.login"))

        login_user(user)
        flash(f"Welcome {user.username}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form, title="Login")


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user, title="Dashboard")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.login"))


@main.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("main.forgot_password"))

        token = s.dumps(email, salt="password-reset")
        link = url_for("main.reset_password", token=token, _external=True)
        send_email(email, "Reset Password", f"Click here to reset your password:\n{link}")

        flash("Password reset link sent! Check your inbox.", "info")
        return render_template("blank2.html", title="Forgot Password")  

    return render_template("forgot_password.html", form=form, title="Forgot Password")


@main.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset", max_age=3600)
    except (SignatureExpired, BadSignature):
        flash("Invalid or expired password reset link.", "danger")
        return redirect(url_for("main.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("main.register"))

        if user.check_password(form.password.data):
            flash("New password cannot be the same as your previous password.", "warning")
            return redirect(url_for("main.reset_password", token=token))

        user.set_password(form.password.data)
        db.session.commit()
        flash("Password reset successful! You can now log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("reset_password.html", form=form, title="Reset Password")


@main.after_request
def add_header(response):
    nocache_routes = [
        "main.login",
        "main.logout",
        "main.register",
        "main.dashboard",
        "main.forgot_password",
        "main.reset_password",
        "main.verify_email",
    ]

    if request.endpoint in nocache_routes:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

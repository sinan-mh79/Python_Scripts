from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from ..models import User, db
from ..forms import RegisterForm, LoginForm
from ..email_utils import send_email
from . import auth
import os

s = URLSafeTimedSerializer(os.getenv("FLASK_SECRET_KEY", "dev_secret"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = s.dumps(email, salt="email-confirm")
        link = url_for("auth.verify_email", token=token, _external=True)
        send_email(email, "Verify Your Email", f"Click here to verify your email:\n{link}")

        return render_template("verify_email.html", title="Verify Email")

    return render_template("register.html", form=form, title="Register")


@auth.route("/verify_email/<token>")
def verify_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
    except SignatureExpired:
        flash("Verification link expired. Please register again.", "warning")
        return redirect(url_for("auth.register"))
    except BadSignature:
        flash("Invalid verification link.", "danger")
        return redirect(url_for("auth.register"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.register"))

    user.is_verified = True
    db.session.commit()
    flash("Your email has been verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("user.dashboard"))

    return render_template("login.html", form=form, title="Login")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))

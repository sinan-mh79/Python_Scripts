from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timedelta
from ..models import User, db
from ..forms import RegisterForm, LoginForm
from ..email_utils import send_email
from . import auth
import os


s = URLSafeTimedSerializer(os.getenv("FLASK_SECRET_KEY", "dev_secret"))


MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 15


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
            flash("That email is already registered. Please log in instead.", "warning")
            return redirect(url_for("auth.login"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send email verification
        token = s.dumps(email, salt="email-confirm")
        link = url_for("auth.verify_email", token=token, _external=True)
        send_email(email, "Verify Your Email", f"Click the link below to verify your email:\n\n{link}")

        flash("A verification link has been sent to your email. Please verify to continue.", "info")
        return render_template("verify_email.html", title="Verify Email")

    return render_template("register.html", form=form, title="Register")


@auth.route("/verify_email/<token>")
def verify_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
    except SignatureExpired:
        flash("Your verification link has expired. Please register again.", "warning")
        return redirect(url_for("auth.register"))
    except BadSignature:
        flash("Invalid verification link.", "danger")
        return redirect(url_for("auth.register"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No user found for this email.", "danger")
        return redirect(url_for("auth.register"))

    user.is_verified = True
    db.session.commit()
    flash("Your email has been successfully verified. You may now log in.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        # Initialize login attempt tracking for this email
        login_data = session.get("login_attempts", {})
        attempts = login_data.get(email, {"count": 0, "locked_until": None})

        # Check if user is currently locked out
        if attempts["locked_until"]:
            if datetime.utcnow() < datetime.fromisoformat(attempts["locked_until"]):
                remaining = datetime.fromisoformat(attempts["locked_until"]) - datetime.utcnow()
                flash(f"Too many failed attempts. Please try again in {int(remaining.total_seconds() // 60)} minutes.", "warning")
                return redirect(url_for("auth.login"))
            else:
                # Reset after lockout period
                attempts = {"count": 0, "locked_until": None}

        # Verify user credentials
        if not user or not user.check_password(password):
            attempts["count"] += 1

            if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
                lock_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_TIME_MINUTES)
                attempts["locked_until"] = lock_until.isoformat()
                flash(f"Too many failed login attempts. Your account is locked for {LOCKOUT_TIME_MINUTES} minutes.", "danger")
            else:
                remaining = MAX_LOGIN_ATTEMPTS - attempts["count"]
                flash(f"Invalid email or password. You have {remaining} attempt{'s' if remaining > 1 else ''} left.", "danger")

            login_data[email] = attempts
            session["login_attempts"] = login_data
            return redirect(url_for("auth.login"))

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("auth.login"))

        # Reset attempts on successful login
        if email in login_data:
            del login_data[email]
            session["login_attempts"] = login_data

        login_user(user)
        
        return redirect(url_for("user.dashboard"))

    return render_template("login.html", form=form, title="Login")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))

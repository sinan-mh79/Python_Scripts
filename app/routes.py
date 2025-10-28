from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_limiter.errors import RateLimitExceeded
import re, secrets
from datetime import datetime
from . import db, limiter
from .models import User
from .email_utils import send_email

main = Blueprint("main", __name__)

# Rate Limit Handler
@main.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    flash("Too many requests! Please wait a moment.", "error")
    return redirect(url_for("main.home"))


# Home page 
@main.route("/")
def home():
    return render_template("home.html")


#Register 
@main.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")

        if not (username and email and password):
            flash("Please fill all fields", "error")
            return redirect(url_for("main.register"))

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            flash("Invalid email format!", "error")
            return redirect(url_for("main.register"))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists", "error")
            return redirect(url_for("main.register"))

        # Password validation
        if len(password) < 8 or not re.search(r"\d", password) \
           or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) \
           or not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", password):
            flash("Weak password! Include upper, lower, number, and special char.", "error")
            return redirect(url_for("main.register"))

        token = secrets.token_urlsafe(16)
        user = User(username=username, email=email, verification_token=token)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        link = url_for("main.verify_email", token=token, _external=True)
        try:
            send_email(email, "Verify your email", f"Click here to verify your account:\n{link}")
            flash("Registration successful! Check your email to verify.", "success")
        except Exception as e:
            print(f"Email error: {e}")
            flash("Email could not be sent. Check console for verification link.", "warning")
            print(f"Verification link: {link}")

        return redirect(url_for("main.login"))

    return render_template("register.html")


# Email verification
@main.route("/verify/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash("Invalid or expired verification link!", "error")
        return redirect(url_for("main.home"))
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    flash("Email verified successfully!", "success")
    return redirect(url_for("main.login"))


# Login 
@main.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

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
                flash("Please verify your email. New link sent.", "warning")
            except Exception as e:
                print(f"Email sending error: {e}")
                flash("Please verify your email. Check console for link.", "warning")
                print(f"Verification link: {link}")
            return redirect(url_for("main.login"))

        session["user_id"] = user.id
        session["username"] = user.username
        flash(f"Welcome {user.username}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


# Dashboard 
@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("main.login"))
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)


#  Logout 
@main.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.home"))


# Forgot Password
@main.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
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

    return render_template("forgot_password.html")


# Reset Password
@main.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("main.home"))

    # Token valid Only 15 minutes 
    if user.token_sent and (datetime.utcnow() - user.token_sent).total_seconds() > 900:
        flash("Reset link expired. Please try again.", "error")
        return redirect(url_for("main.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("main.reset_password", token=token))

        user.set_password(password)
        user.reset_token = None
        user.token_sent = None
        db.session.commit()
        flash("Password reset successful!", "success")
        return redirect(url_for("main.login"))

    return render_template("reset_password.html", token=token)

from flask import render_template, redirect, url_for, flash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from ..models import User, db
from ..forms import ForgotPasswordForm, ResetPasswordForm
from ..email_utils import send_email
from flask_login import current_user
from . import main
import os

s = URLSafeTimedSerializer(os.getenv("FLASK_SECRET_KEY", "dev_secret"))


@main.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("main.forgot_password"))

        token = s.dumps(email, salt="password-reset")
        link = url_for("main.reset_password", token=token, _external=True)
        send_email(email, "Reset Your Password", f"Click here to reset your password:\n{link}")

        return render_template("forgot_email_sent.html", title="Forgot Password")

    return render_template("forgot_password.html", form=form, title="Forgot Password")


@main.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset", max_age=3600)
    except SignatureExpired:
        flash("Reset link expired. Please request a new one.", "warning")
        return redirect(url_for("main.forgot_password"))
    except BadSignature:
        flash("Invalid password reset link.", "danger")
        return redirect(url_for("main.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.register"))  

    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.password.data

        if user.check_password(new_password):
            flash("New password cannot be the same as your old one.", "warning")
            return redirect(url_for("main.reset_password", token=token))

        user.set_password(new_password)
        db.session.commit()
        flash("Your password has been reset successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))  

    return render_template("reset_password.html", form=form, title="Reset Password")

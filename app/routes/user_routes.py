from flask import render_template
from flask_login import login_required, current_user
from . import user  

@user.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user=current_user,
        title="Dashboard"
    )

@user.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        user=current_user,
        title="Profile"
    )

@user.route("/projects")
@login_required
def projects():
    return render_template(
        "projects.html",
        user=current_user,
        title="Projects"
    )

@user.route("/contact")
@login_required
def contact():
    return render_template(
        "contact.html",
        user=current_user,
        title="Contact"
    )

@user.route("/skills")
@login_required
def skills():
    return render_template(
        "skills.html",
        user=current_user,
        title="Skills"
    )

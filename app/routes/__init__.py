from flask import Blueprint

main = Blueprint("main", __name__)
user = Blueprint("user", __name__)
auth = Blueprint("auth", __name__)

from . import auth_routes, password_routes, user_routes, general_routes

from flask import request

@main.after_request
def add_header(response):
    nocache_routes = [
        "auth.login",
        "auth.logout",
        "auth.register",
        "auth.forgot_password",
        "auth.reset_password",
        "auth.verify_email",
    ]

    if request.endpoint in nocache_routes:
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

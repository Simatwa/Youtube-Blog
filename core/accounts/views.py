from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask import (
    request,
    render_template,
    flash,
    redirect,
    url_for,
    make_response,
    abort,
)
from .forms import (
    UserLoginForm,
    VerifyUserForm,
    ResetPasswordForm,
    ResetPasswordFormNew,
)
from core.accounts import app
from core.app import application, send_mail, bcrypt
from core.accounts.models import db, Admin1
from sqlalchemy import or_
from uuid import uuid4
from urllib.parse import urlsplit, quote

login_manager = LoginManager()
login_manager.init_app(application)


@login_manager.user_loader
def load_user(user_id):
    """Loads user id"""
    # return Admin1.query.get(user_id)
    return Admin1.query.get(user_id)


class Utils:
    @staticmethod
    def hash_password(paswd):
        """Hashes password"""
        return bcrypt.generate_password_hash(paswd).decode('utf-8')

    @staticmethod
    def login_not_required(
        message="You've already logged in!",
        flash_category="warn",
        next="/",
    ):
        """Ensures only unauthenticated user access the view"""

        def decorator(func):
            def main(*args, **kwargs):
                if current_user.is_authenticated:
                    flash(message, flash_category)
                    return redirect(next)
                else:
                    return func(*args, **kwargs)

            return main

        return decorator

    @staticmethod
    def generate_verification_token():
        """Generatws verification token"""
        return str(uuid4())[:8]


class Accounts:
    """Handle views related to account"""

    @classmethod
    @Utils.login_not_required()
    def create_user(cls):
        """Create new user"""
        if request.method == "GET":
            pass
            # Send user_creation_form
        else:
            pass
            # Verify credentials

    @classmethod
    @Utils.login_not_required()
    def login_user(cls, login=False):
        """Logins user'"""
        form = UserLoginForm()
        if request.method == "GET" or login:
            return render_template("login.html", form=form)
        else:
            if form.validate_on_submit():
                identifier = form.identifier.data
                password = form.password.data
                # category = form.category.data
                """
                try_user = Admin1.query.filter(
                    Admin1.password == Utils.hash_password(password),
                    or_(
                        Admin1.email == identifier,
                        Admin1.phone_no == identifier,
                        Admin1.index_no
                        == (int(identifier) if identifier.isdigit() else identifier),
                    ),
                ).first()
                """
                try_user = Admin1.query.filter_by(
                    email=identifier
                ).first()

                if try_user and bcrypt.check_password_hash(try_user.password, password):
                    try_user.is_active = True
                    if not try_user.is_authenticated:
                        """User address is not verified"""
                        try_user.is_anonymous = False
                        db.session.commit()
                        login_user(try_user)
                        flash("Kindly verify your email address", "warn")
                        return redirect(url_for("accounts.verify_user_address"))
                    flash("Logged in successful", "info")
                    try_user.is_authenticated = True
                    db.session.commit()
                    login_user(try_user)	
                    return redirect(url_for('admin.index'))
                    
                else:
                    flash("Incorrect identifier or password!", "error")
                    return render_template("login.html", form=form)
            else:
                return render_template("login.html", form=form)

    @classmethod
    @Utils.login_not_required(message="Your account is already verified!")
    def verify_user(cls):
        form = VerifyUserForm()
        target_user = Admin1.query.filter_by(
            id=current_user.get_id()
        ).first_or_404()
        assert target_user.is_authenticated == False, abort(401)

        if request.method == "GET":
            target_user.token = Utils.generate_verification_token()
            db.session.commit()
            # Send the token to user's mail address
            html = f"""
			<!DOCTYPE html>
			<head>
			<link rel="stylesheet" href="w3.css"></link>
			<meta name="viewport" content="width=device-width, initial-scale=1.0"></meta>
			<title>Confirmation Token</title>
			</head>
			<body>
			<div class="w3-container">
			<h2>Verify Email  Address</h2>
			<p>Hello <strong>{target_user.fname}</strong>, your confirmation token is:
			 <div class="w3-panel w3-steal w3-center w3-text-red">{target_user.token}</div></p>
			 </div></body></html>
			 """
            send_mail("Confirmation Token", html=html, recipients=[target_user.email])
            return render_template("verify_user.html", form=form)
        else:
            if form.validate_on_submit():
                if form.token.data == target_user.token:
                    flash("Verification succeeded!", "info")
                    target_user.is_authenticated = True
                    db.session.commit()
                    return redirect(url_for("home"))
                else:
                    flash("Invalid token!", "error")
                    return render_template("verify_user.html", form=form)
            else:
                return render_template("verify_user.html", form=form)

    @classmethod
    @Utils.login_not_required()
    def reset_password(cls, return_form=False):
        """Takes initial password reset process"""
        form = ResetPasswordForm()
        if request.method == "GET" or return_form:
            return render_template("reset_user_password_enter_email.html", form=form)
        else:
            if form.validate_on_submit():
                user_exist = Admin1.query.filter_by(email=form.email.data).first()
                if user_exist:
                    user_exist.token = Utils.generate_verification_token()
                    db.session.commit()
                    send_mail(
                        "Password Reset Code",
                        body="Hello, to reset your password enter this token on the Token field. %s . It will expire in 20 minutes time."
                        % user_exist.token,
                        recipients=[user_exist.email],
                    )
                    flash("We've sent 8 code token to the Email address.")
                    response = make_response(
                        render_template(
                            "reset_user_password_enter_token.html",
                            form=ResetPasswordFormNew(),
                        )
                    )
                    response.set_cookie("mail", user_exist.email, max_age=60 * 20)
                    return response
                else:
                    flash("User with that email address doesn't exist!", "warn")
                    return cls.reset_password(return_form=True)
            else:
                return render_template(
                    "reset_user_password_enter_email.html",
                    form=form,
                )

    @classmethod
    @Utils.login_not_required()
    def reset_password_new(cls):
        """Completes password reset process"""
        email = request.cookies.get("mail")
        if not email:
            return redirect(url_for("accounts.reset_password"))

        form = ResetPasswordFormNew()
        if form.validate_on_submit():
            user_exist = Admin1.query.filter_by(
                email=email, token=form.token.data
            ).first()
            if user_exist:
                user_exist.password = Utils.hash_password(form.password.data)
                user_exist.token = False
                db.session.commit()
                flash("Password reset successfully!", "info")
                response = make_response(redirect(url_for("home")))
                response.delete_cookie("mail")
                return response
            else:
                flash("Invalid Authentication token!", "warn")
                return render_template(
                    "reset_user_password_enter_token.html", form=form
                )
        else:
            return render_template("reset_user_password_enter_token.html", form=form)

    @classmethod
    @login_required
    def logout_user(cls):
        """Logs-out user"""
        logout_user()
        return redirect(url_for("home"))


login_manager.login_view = "accounts.login_user"
login_manager.login_message = "Kindly login first!"
login_manager.login_message_category = "warn"

accounts = Accounts()

app.add_url_rule(
    "/create-account",
    view_func=accounts.create_user,
    endpoint="create_account",
)
app.add_url_rule(
    "/login",
    view_func=accounts.login_user,
    endpoint="login_user",
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/verify-address",
    view_func=accounts.verify_user,
    endpoint="verify_user_address",
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/reset-password",
    view_func=accounts.reset_password,
    endpoint="reset_password",
    methods=["GET", "POST"],
)
app.add_url_rule(
    "/reset-password-new",
    view_func=accounts.reset_password_new,
    endpoint="reset_password_new",
    methods=["GET", "POST"],
)
app.add_url_rule("/logout", view_func=accounts.logout_user, endpoint="logout_user")

# Calls the admin view

from core.accounts.admin import admin

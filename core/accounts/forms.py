from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class CreateUserForm(FlaskForm):
    """Not necessary at the moment"""

    pass
    # Will be handled at admin level


class UserLoginForm(FlaskForm):
    identifier = StringField(
        validators=[DataRequired()],
        render_kw={"class": "w3-input", "placeholder": "E-mail address"},
    )
    password = PasswordField(
        validators=[
            DataRequired(message="Enter your password"),
            Length(
                min=6, max=20, message="Characters must be between %(min)d  to %(max)d"
            ),
        ],
        render_kw={"class": "w3-input", "placeholder": "Password"},
    )
    # category = SelectField(label="Login as",validators=[DataRequired(message="Select category")],render_kw={"class":"w3-select"})

    remember_me = BooleanField(label="Remember me", render_kw={"class": "w3-check"})
    Login = SubmitField(render_kw={"class": "w3-button w3-steal w3-block w3-ripple"})


class VerifyUserForm(FlaskForm):
    token = StringField(
        label="Enter the 8-codes-token sent to your Email address",
        validators=[
            DataRequired("Token Can't be null"),
            Length(
                min=7, max=9, message="Token must contain %(min)d-%(max)d characters"
            ),
        ],
        render_kw={
            "placeholder": "CODE",
            "class": "w3-input",
            "style": "max-width:120px",
        },
    )
    Verify = SubmitField(render_kw={"class": "w3-button w3-steal w3-ripple"})


class ResetPasswordForm(FlaskForm):
    email = StringField(
        label="Enter registered email address",
        validators=[
            DataRequired(message="Email address is required!"),
            Email(message="Enter valid email address!"),
        ],
        render_kw={"placeholder": "e.g example123@gmail.com", "class": "w3-input"},
    )
    Reset = SubmitField(render_kw={"class": "w3-btn w3-ripple w3-steal w3-block"})


class ResetPasswordFormNew(FlaskForm):
    token = StringField(
        validators=[
            DataRequired(message="Token cannot be null!"),
            Length(
                min=8, max=9, message="Token must be %(min)d to %(max)d characters!"
            ),
        ],
        render_kw={
            "placeholder": "8 - Code - Token",
            "class": "w3-input",
            "style": "max-width:130px",
        },
    )
    password = PasswordField(
        validators=[DataRequired(message="Password is required!")],
        render_kw={"placeholder": "Password", "class": "w3-input"},
    )
    confirm_password = PasswordField(
        validators=[
            DataRequired(message="Reconfirm password"),
            Length(
                min=6,
                max=20,
                message="Password must contain %(min)d to %(max)d characters!",
            ),
            EqualTo("password", message="Password must match!"),
        ]
    )
    Ok = SubmitField(render_kw={"class": "w3-button w3-steal w3-ripple"})

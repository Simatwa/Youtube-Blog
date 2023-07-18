from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, Length


class SearchForm(FlaskForm):
    """Not necessary at the moment"""

    query = StringField(
        validators=[DataRequired(message="Enter query")],
        render_kw={"placeholder": "Search blog.."},
    )


class CommentForm(FlaskForm):
    blog_uuid = HiddenField()
    username = StringField(
        label="Username",
        validators=[
            DataRequired("Name can't be null"),
            Length(
                min=1, max=20, message="Name must contain atleast %(max)d characters"
            ),
        ],
        render_kw={
            "class": "w3-input w3-round",
            "placeholder": "First, second or both",
        },
    )
    email = StringField(
        label="Email address",
        validators=[
            DataRequired("Email address required!"),
            Email(message="Enter valid email address"),
        ],
        render_kw={"class": "w3-input w3-round", "placeholder": "example@gmail.com"},
    )
    content = TextAreaField(
        label="Your message",
        validators=[
            DataRequired(
                message="Feedback can't be null!",
            ),
            Length(
                min=2,
                max=500,
                message="Message must contain %(min)d-%(max)d characters.",
            ),
        ],
        render_kw={
            "class": "w3-input",
            "placeholder": "Reaction in detail...",
            "rows": 5,
        },
    )
    mood = SelectField(
        label="Select Mood",
        choices=([("grin", "Happy"), ("frown", "Sad")]),
        validators=[DataRequired("Select your mood")],
        render_kw={"class": "w3-input"},
    )
    send = SubmitField(label="Send")

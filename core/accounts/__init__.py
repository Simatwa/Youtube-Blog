from flask import Blueprint

app = Blueprint(
    "accounts",
    __name__,
    template_folder="templates",
)

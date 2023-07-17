import os

basedir = os.path.abspath(os.path.dirname(__file__))


def get(key, default=None):
    return os.environ.get(key, default)


SQLALCHEMY_DATABASE_URI = get(
    "SQLALCHEMY_DATABASE_URI",
    "sqlite:///sqlite3.db",
)

SECRET_KEY = get(
    "SECRET_KEY",
    "halwu2yhw8bw817bq7ta5q61bw6",
)

RECAPTCHA_PUBLIC_KEY = get(
    "RECAPTCHA_PUBLIC_KEY",)

RECAPTCHA_PRIVATE_KEY = get(
    "RECAPTCHA_PRIVATE_KEY",)


FLASK_ADMIN_SWATCH = get("FLASK_ADMIN_SWATCH", "paper")


MAIL_SERVER = get("MAIL_SERVER", "smtp.gmail.com")

MAIL_PORT = get("MAIL_PORT", 465)

MAIL_USERNAME = get("MAIL_USERNAME")

MAIL_PASSWORD = get("MAIL_PASSWORD")

MAIL_USE_TLS = get(
    "MAIL_USE_TLS",
    False,
)

MAIL_USE_SSL = get(
    "MAIL_USE_SSL",
    True,
)

MAIL_DEFAULT_SENDER = get("MAIL_DEFAULT_SENDER", "smartwacaleb@gmail.com")


## User database config

BLOG_IMAGES_DIR = os.path.join(basedir, "static/images/blog")

if not os.path.isdir(BLOG_IMAGES_DIR):
    os.makedirs(BLOG_IMAGES_DIR)
    ## Creates blog images directory

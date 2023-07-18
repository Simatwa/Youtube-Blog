from .app import application

# Register blueprints here

from .accounts.views import app as accounts_view
from .blog.views import app as blog_view

application.register_blueprint(accounts_view, url_prefix="/accounts", cli_group="user")
application.register_blueprint(blog_view, url_prefix="/", cli_group="blog")

from flask_migrate import Migrate

from .models import db

# Migrates db schema
migrate = Migrate()

migrate.init_app(application, db)

# Creates db schema

with application.app_context():
    db.create_all()

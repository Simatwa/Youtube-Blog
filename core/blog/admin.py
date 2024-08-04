from core.admin import admin
from core.models import db
from core.app import application, bcrypt, FILES_DIR
from core.blog import app
from core.blog.models import Blog, Subscriber, Comment, Category, SocialMedia, Messages
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import flash, redirect, url_for, abort
from flask_admin.form import FileUploadField, SecureForm
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileRequired, FileAllowed
import click
from flask_login import login_required, current_user
from os import path
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import text


class LocalUtils:
    @staticmethod
    def generate_filename(obj, file_data):
        filename = secure_filename(file_data.filename)
        time = datetime.utcnow()
        month = str(time.month)
        year = str(time.year)
        return path.join(
            obj.authors[0].name, obj.categories[0].name, year, month, filename
        )


class BlogModelView(ModelView):
    """Blog model view"""

    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    page_size = 50
    can_export = True
    can_view_details = True
    column_default_sort = ("created_on", True)
    form_excluded_columns = [
        "likes",
        "views",
        "comments",
        "uuid",
        "created_on",
        "lastly_modified",
        "html_content",
        "hash",
    ]
    column_searchable_list = [
        "title",
        "intro",
        "content",
        "comments.content",
    ]
    column_filters = [
        "title",
        "content",
        "categories.name",
        "authors.name",
        "link_only",
        "views",
        "likes",
        "id",
        "link",
        "accept_comments",
        "is_published",
        "created_on",
    ]
    column_exclude_list = [
        "content",
        "hash",
        "link",
        "intro",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
        "cover_photo",
        "file_1",
        "file_2",
        "lastly_modified",
        "is_markdown",
        "html_content",
    ]
    column_editable_list = [
        "is_published",
        "display_ads",
        "views",
        "likes",
        "accept_comments",
    ]

    column_details_exclude_list = [
        "hash",
        "html_content",
    ]

    column_labels = dict(is_notified="Is Mailed")
    form_base_class = SecureForm

    form_args = {
        "title": {
            "render_kw": {
                "placeholder": "Article title",
            },
        },
        "content": {
            "render_kw": {
                "placeholder": "Blog content...",
            },
        },
        "categories": {
            "render_kw": {
                "placeholder": "Select categories",
            },
            "validators": [DataRequired(message="Select categories")],
        },
        "link": {
            "render_kw": {
                "placeholder": "Youtube video link or video id",
            },
        },
        "authors": {
            "validators": [
                DataRequired(
                    message="Select your name",
                ),
            ],
        },
        "intro": {
            "label": "Synopsis",
            "render_kw": {
                "placeholder": "Brief, informative & catchy...",
            },
        },
        "link_only": {
            "label": "Don't index this article on website pages.",
        },
    }

    form_widget_args = {
        "content": {
            "rows": 30,
        },
    }

    form_extra_fields = {
        "cover_photo": FileUploadField(
            "Cover photo",
            base_path=FILES_DIR,
            validators=[
                FileAllowed(
                    ["jpg", "png", "jpeg", "svg", "gif", "webp"], message="Images only!"
                ),
            ],
            namegen=LocalUtils.generate_filename,
        ),
        "image_1": FileUploadField(
            "1st Image",
            base_path=FILES_DIR,
            validators=[
                FileAllowed(
                    ["jpg", "png", "jpeg", "svg", "gif", "webp"], message="Images only!"
                ),
            ],
            namegen=LocalUtils.generate_filename,
        ),
        "image_2": FileUploadField(
            "2nd Image",
            base_path=FILES_DIR,
            validators=[
                FileAllowed(
                    ["jpg", "png", "jpeg", "svg", "gif", "webp"], message="Images only!"
                ),
            ],
            namegen=LocalUtils.generate_filename,
        ),
        "image_3": FileUploadField(
            "3rd Image",
            base_path=FILES_DIR,
            validators=[
                FileAllowed(
                    ["jpg", "png", "jpeg", "svg", "gif", "webp"], message="Images only!"
                ),
            ],
            namegen=LocalUtils.generate_filename,
        ),
        "image_4": FileUploadField(
            "4th Image",
            base_path=FILES_DIR,
            validators=[
                FileAllowed(
                    ["jpg", "png", "jpeg", "svg", "gif", "webp"], message="Images only!"
                ),
            ],
            namegen=LocalUtils.generate_filename,
        ),
        "file_1": FileUploadField(
            "1st file",
            base_path=FILES_DIR,
            validators=[],
            namegen=LocalUtils.generate_filename,
        ),
        "file_2": FileUploadField(
            "2nd file",
            base_path=FILES_DIR,
            validators=[],
            namegen=LocalUtils.generate_filename,
        ),
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


class CommentModelView(ModelView):
    """Comment Model View"""

    page_size = 50
    can_export = False
    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    can_view_details = True
    column_default_sort = ("id", True)
    column_filters = [
        "created_on",
        "username",
        "user_email",
        "created_on",
        "mood",
        "likes",
        "blogs.title",
    ]
    column_searchable_list = ["content", "blogs.title"]
    column_exclude_list = ["lastly_modified"]
    form_excluded_columns = ["created_on", "lastly_modified"]
    form_base_class = SecureForm

    form_args = {
        "username": {
            "render_kw": {
                "placeholder": "User",
            },
        },
        "user_email": {
            "render_kw": {
                "placeholder": "example@gmail.com",
            },
            "validators": [Email(message="Enter valid email address!")],
        },
        "content": {
            "render_kw": {
                "placeholder": "Text message...",
            },
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


class SubscriberModelView(ModelView):
    """Subscriber model view"""

    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    page_size = 50
    can_view_details = True
    column_default_sort = ("id", True)
    form_excluded_columns = ["created_on"]
    column_filters = ["created_on"]
    column_searchable_list = ["email"]
    column_editable_list = ["is_verified"]
    form_base_class = SecureForm

    form_args = {
        "email": {
            "label": "Email address",
            "render_kw": {
                "placeholder": "example@gmail.com",
            },
            "validators": [Email(message="Enter valid email address!")],
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


class CategoryModelView(ModelView):
    """Categorya Model view"""

    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("id", True)
    form_excluded_columns = ["created_on"]
    column_searchable_list = ["name"]
    column_filters = ["created_on"]
    column_editable_list = [
        "display_on_menu",
        "color",
        "display_position",
        "detail",
        "icon",
    ]
    form_base_class = SecureForm

    form_args = {
        "name": {
            "render_kw": {
                "placeholder": "Enter name",
            },
        },
        "detail": {
            "render_kw": {
                "placeholder": "What's this category about?",
            },
        },
        "icon": {
            "render_kw": {
                "placeholder": "Fon-awesome icon name",
            },
        },
        "color": {
            "render_kw": {
                "placeholder": "On hover color",
            },
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


class SocialMediaModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    page_size = 50
    column_default_sort = ("id", True)
    form_excluded_columns = ["created_on"]
    column_searchable_list = ["name", "link"]
    filter = ["color"]
    column_editable_list = ["small_screen", "link", "color"]
    form_base_class = SecureForm

    form_args = {
        "name": {
            "render_kw": {
                "placeholder": "Social media site name",
            },
        },
        "link": {
            "render_kw": {
                "placeholder": "Url pointing to your profile",
            },
        },
        "color": {
            "render_kw": {
                "placeholder": "Color for displaying the icon",
            },
        },
        "small_screen": {
            "label": "Display on small devices?",
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


class MesssagesModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50
    form_excluded_columns = ["created_on"]
    # column_exclude_list = ["lastly_modified"]
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("id", True)
    column_searchable_list = ["title", "content"]
    column_filters = ["created_on", "send", "id"]
    column_labels = dict(send="Sent")

    form_args = {
        "content": {
            "render_kw": {
                "placeholder": "Html or Markdown format",
            },
        },
    }

    form_widget_args = {
        "content": {
            "rows": 10,
        },
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "danger")
        return redirect(url_for("home"))


@click.command("sql")
@click.option("-q", "--query", help="SQL Query")
@click.option("--once", is_flag=True, help="Run one query and exit.")
@click.option("--index", is_flag=True, help="Add index to displayed rows")
def run_sql_statements(query: str, once: bool, index: bool):
    """Run SQL statements against database"""
    init_run = False
    while True:
        try:
            q = query if query and not init_run else input("sql: ")
            results = db.session.execute(text(q))
            if results:
                for count, entry in enumerate(results):
                    print(f"{count} - " if index else "", entry)
            else:
                print("-----ok-----")
            db.session.commit()
        except KeyboardInterrupt:
            print("^ Quitting")
            break
        except Exception as e:
            print(e.args[1] if e.args and len(e.args) > 1 else e)
        finally:
            if once:
                break


@click.command("clear-migrations")
@click.confirmation_option(
    "-y",
    "--yes",
    is_flag=True,
    help="Okay to confirmation",
    prompt="Are you sure to clear migrations to its entirity",
)
def clear_migrations():
    """Clear migrations and its metadata"""
    click.secho("Clearing alembic's matadata in database.", fg="yellow")
    try:
        db.session.execute(text("DROP TABLE alembic_version"))
        db.session.commit()
    except:
        pass
    target_dir = "migrations"
    if path.isdir(target_dir):
        click.secho("Clearing migrations directory.", fg="yellow")
        import shutil

        shutil.rmtree(target_dir)


admin.add_view(BlogModelView(Blog, db.session, name="Articles"))
admin.add_view(CommentModelView(Comment, db.session, name="Comments"))
admin.add_view(SubscriberModelView(Subscriber, db.session, name="Subscribers"))
admin.add_view(CategoryModelView(Category, db.session, name="Categories"))
admin.add_view(SocialMediaModelView(SocialMedia, db.session, name="Accounts"))
admin.add_view(MesssagesModelView(Messages, db.session, name="Messages"))
application.cli.add_command(run_sql_statements)
application.cli.add_command(clear_migrations)

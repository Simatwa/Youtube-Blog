from core.models import db
from core.accounts.models import Admin1, AppDetail
from datetime import datetime
from os import path, rename, remove
from core.app import FILES_DIR, send_mail
from core.accounts.models import AppDetail, default_cover_photo
import logging
from slugify import slugify
from flask import url_for, flash
from core.app import generate_uuid as gen_uuid
from flask_login import current_user
from core.app import markdown_extensions
import markdown
import re

fullpath = lambda r_path: path.join(FILES_DIR, r_path)


class Blog(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    authors = db.relationship(
        "Admin1",
        secondary="blog_admin1",
        lazy=True,
        cascade="all, delete",
        passive_deletes=True,
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(
        db.Text,
    )
    categories = db.relationship(
        "Category",
        secondary="blog_category",
        backref="blogs",
        lazy=True,
        cascade="all, delete",
        passive_deletes=True,
    )
    intro = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship(
        "Comment",
        backref="blogs",
        lazy=True,
        cascade="all, delete",
        passive_deletes=True,
    )
    uuid = db.Column(db.String(60), nullable=False, unique=True)
    cover_photo = db.Column(db.String(60), nullable=True, default=default_cover_photo)
    image_1 = db.Column(db.String(60), nullable=True)
    image_2 = db.Column(db.String(60), nullable=True)
    image_3 = db.Column(db.String(60), nullable=True)
    image_4 = db.Column(db.String(60), nullable=True)
    file_1 = db.Column(db.String(60), nullable=True)
    file_2 = db.Column(db.String(60), nullable=True)
    link = db.Column(db.String(20), nullable=True)
    trending = db.Column(db.Boolean(), default=False)
    is_markdown = db.Column(db.Boolean(), default=True)
    is_published = db.Column(db.Boolean(), default=False)
    is_notified = db.Column(db.Boolean(), default=False)
    display_ads = db.Column(db.Boolean(), default=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    lastly_modified = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return "<Blog %r>" % self.id

    def __str__(self):
        return self.title


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(
        db.String(
            20,
        ),
        nullable=False,
    )
    user_email = db.Column(db.String(30), nullable=False)
    content = db.Column(
        db.Text,
        nullable=False,
    )
    likes = db.Column(db.Integer, default=0)
    mood = db.Column(db.String(10), default="grin")
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    lastly_modified = db.Column(
        db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    blog_id = db.Column(
        db.Integer,
        db.ForeignKey("blogs.id", onupdate="CASCADE", ondelete="SET NULL"),
        autoincrement=True,
    )

    def __repr__(self):
        return "<Comment %r>" % self.id

    def __str__(self):
        return self.username


class Subscriber(db.Model):
    __tablename__ = "subscribers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    token = db.Column(db.String(40), nullable=True)
    is_verified = db.Column(db.Boolean(), default=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<Subscriber %r>" % self.id

    def __str__(self):
        return self.email


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(15), nullable=True)
    color = db.Column(db.String(15), default="green")
    display_position = db.Column(db.Integer, default=0,)
    display_on_menu = db.Column(db.Boolean(), default=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    	
    def __repr__(self):
        return "<Category %r>" % self.id

    def __str__(self):
        return self.name


class BlogCategory(db.Model):
    # __tablename__="blogcategories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blog_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "blogs.id",
        ),
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
        ),
    )

    def __repr__(self):
        return "<BlogCategory %r>" % self.id


class SocialMedia(db.Model):
    __tablename__ = "socialmedia"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    color = db.Column(db.String(15), nullable=False)
    small_screen = db.Column(db.Boolean(), default=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "<SocialMedia %r>" % self.id

    def __init__(self):
        return self.name


class BlogAdmin1(db.Model):
    """Links Blogs & Admin1 M:M"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blog_id = db.Column(db.ForeignKey("blogs.id"))
    admin_id = db.Column(db.ForeignKey("admins.id"))


class LocalUtils:
    """Utilities class"""

    @staticmethod
    def generate_html_tag(filename: str):
        extension = path.splitext(filename)[1].lower()
        # image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".3gp"]
        audio_extensions = [".mp3", ".wav", ".flac", ".ogg"]
        # if extension in image_extensions:
        # resp = f'<img class="w3-image" src="{filename}" alt="Image">'
        if extension in video_extensions:
            resp = f"""
	   	<div class="w3-center w3-padding">	   	
	   	    <video  controls>
	   	   <source src="{filename}" type="video/{extension[1:]}">
	   	</video>
	   	</div>"""
        elif extension in audio_extensions:
            resp = f"""
	   	<div class="w3-center w3-padding">
	   	  <audio controls>
	   	  <source src="{filename}" type="audio/{extension[1:]}">
	   	</audio>
	   	</div>"""
        else:
            resp = filename
        return resp.strip()


class LocalEventListener:
    @staticmethod
    def delete_images(mapper, connections, target):
        """Delete blog images"""
        all_files = [
            target.cover_photo,
            target.image_1,
            target.image_2,
            target.image_3,
            target.image_4,
            target.file_1,
            target.file_2,
        ]
        appdetails = AppDetail.query.get(1)
        for entry in all_files:
            if (
                not entry
                or entry
                and entry in [appdetails.logo, appdetails.cover_photo]
            ):
                continue
            try:
                remove(fullpath(entry))
            except Exception as e:
                logging.error("Failed to delete file -  {}".format(e.args))

    @staticmethod
    def generate_uuid(mapper, connections, target):
        """Generates uuid for each blog"""
        if target.uuid and not " " in target.uuid:
            # Effective to one-word-titled article too
            return
        uuid = slugify(target.title)
        not_unique = True
        count = 1
        if not Blog.query.filter_by(uuid=uuid).first():
            target.uuid = uuid
            return
        while not_unique:
            if not Blog.query.filter_by(uuid=uuid + "-" + str(count)).first():
                target.uuid = uuid + "-" + str(count)
                not_unique = False
            count += 1

    @staticmethod
    def confirm_email(mapper, connections, target):
        appdetail = AppDetail.query.filter_by(id=1).first()
        gen_link = lambda abs_url: appdetail.url + abs_url
        target.token = gen_uuid()
        message = f"""
		<head>
		  <meta name="viewport" content="width=device-width, initial-scale=1.0">
		  </meta
		</head>
		<h3>Confirm Subscription to {appdetail.name}</h3>
		<p> Thank you for showing interest in our contents.</p>
		<p>Click the button below to confirm subscription</p>
		<center>
		<div style="background-color:teal; max-width:80%;min-height:5vh;border-radius:10px;">
		 <a style="color:white;text-decoration:none;font-weght:bold;font-size:120%;text-align:center" href="{ gen_link(url_for('blogs.confirm_email', token=target.token)) }">Confirm</a>
		</div>
		</center>
		<p> If the link doesn't work try out this { gen_link(url_for('blogs.confirm_email',token=target.token)) }</p>
		<div style="text-align:center;font-weight:bold;color:red;">
		 <h4>{ appdetail.name } © { datetime.now().year }</h4>
		 <p style="color:blue">{ appdetail.slogan }</p>
		</div>
		"""
        send_mail("Confirm Subscription", html=message, recipients=[target.email])

    @staticmethod
    def mail_blog(mapper, connections, target):
        """Mails the update to subscribers"""
        if target.is_published:
            if target.is_notified:
                return
        else:
            return
        appdetail = AppDetail.query.filter_by(id=1).first()
        gen_link = lambda abs_url: appdetail.url + abs_url
        img = (
            """<iframe width="80%" height="auto" src="https://www.youtube.com/embed/{target.link}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; 
		encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
		"""
            if target.link
            else f"""<img src="{gen_link(url_for('static', filename='files/'+target.cover_photo))}" max-width="80%" height="auto" alt="{target.cover_photo}">
		</img>"""
            if target.cover_photo
            else ""
        )

        message = f"""
		<h3>{ ' | '.join([str(category) for category in target.categories]) } - New Post </h3>
		<center>
		{img}
		</center>
		<p>{target.intro}</p>
		<p style="text-align:center">To read this in detail <a href="{gen_link(url_for('blogs.blog_view', uuid=target.uuid))}">click here.</a></p>"""

        subscribers_entry = (
            Subscriber.query.filter_by(is_verified=True)
            .with_entities(Subscriber.email)
            .all()
        )
        subscribers = [subscriber[0] for subscriber in subscribers_entry if subscriber]
        if subscribers:
            logging.info(
                f'Mailing "{target.title}" to {len(subscribers)} subscriber(s)'
            )
            send_mail(subject=target.title, recipients=subscribers, html=message)
            target.is_notified = True
            flash(
                "Article has been mailed to %d subscriber(s)." % len(subscribers),
                "success",
            )
        else:
            pass

    @staticmethod
    def add_w3_styles(target):
        """Adds w3-styles to htmls"""
        tags_dict = {
            "<img": '<IMG class="w3-image w3-center w3-padding w3-hover-opacity"',
            "<table": '<TABLE class="w3-table-all w3-center w3-hoverable w3-responsive"',
            # "<thead" : '<THEAD class="w3-orange"',
        }
        for tag in tags_dict:
            target.content = re.sub(tag, tags_dict[tag], target.content)

    @staticmethod
    def format_markdown_article(mapper, connections, target):
        if target.is_markdown and target.content:
            target.content = (
                target.content.replace("%(", "(}}}}")
                .replace("%", "%%")
                .replace("(}}}}", "%(")
            )
            gen_file_link = lambda name: url_for(
                "static", filename="files/" + str(name)
            )
            kwargs = {
                "file_1": LocalUtils.generate_html_tag(gen_file_link(target.file_1)),
                "file_2": LocalUtils.generate_html_tag(gen_file_link(target.file_2)),
            }
            image_names = [
                target.cover_photo,
                target.image_1,
                target.image_2,
                target.image_3,
                target.image_4,
            ]
            for count, name in enumerate(image_names):
                if count == 0:
                    kwargs["cover_photo"] = gen_file_link(name)
                else:
                    kwargs[f"image_{count}"] = gen_file_link(name)

            target.content = markdown.markdown(
                target.content % kwargs, extensions=markdown_extensions
            )
            LocalEventListener.add_w3_styles(target)


db.event.listen(Blog, "before_insert", LocalEventListener.generate_uuid)
db.event.listen(Blog, "before_update", LocalEventListener.generate_uuid)

db.event.listen(Blog, "before_insert", LocalEventListener.mail_blog)
db.event.listen(Blog, "before_update", LocalEventListener.mail_blog)

db.event.listen(Blog, "before_insert", LocalEventListener.format_markdown_article)
db.event.listen(Blog, "before_update", LocalEventListener.format_markdown_article)

db.event.listen(Blog, "before_delete", LocalEventListener.delete_images)

db.event.listen(Subscriber, "before_insert", LocalEventListener.confirm_email)

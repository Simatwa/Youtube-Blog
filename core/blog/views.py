from core.blog import app
from flask import (
    render_template,
    request,
    flash,
    jsonify,
    make_response,
    redirect,
    url_for,
)
from core.blog.models import Blog, Category, Subscriber, SocialMedia, Comment
from core.blog.forms import CommentForm
from sqlalchemy import or_, desc, not_
from core.models import db
from flask_login import login_required, current_user
from core.accounts.models import AppDetail, Admin1, Advertisement
from core.app import application
from datetime import datetime, timedelta
from core.accounts.models import Advertisement
import re
from flask import session, abort


class LocalUtils:
    """Module based utility defs"""

    @staticmethod
    def add_latest_adverts(blog: Blog):
        """Append ads to blog content"""
        ads_tag = r"{ads}"
        preprocessor_one = blog.html_content
        if not preprocessor_one:
            return blog
        if not blog.display_ads:
            # Drop all tags
            blog.content = re.sub(ads_tag, "", preprocessor_one)
            return blog
        ads_space_count = preprocessor_one.count(ads_tag)
        ads_code_available = [
            ads_code[0]
            for ads_code in Advertisement.query.filter_by(
                is_active=True, is_script=False
            )
            .order_by(desc(Advertisement.id))
            .with_entities(Advertisement.content)
            .all()
        ]
        # Ensures length of ads_space_count==ads_code_available
        for x in range(ads_space_count):
            if len(ads_code_available) < ads_space_count:
                if x > len(ads_code_available) - 1:
                    ads_code_available.append("")
                else:
                    # Ensures we don't duplicate alot
                    if x != 0:
                        # Duplicate the available ads_code
                        ads_code_available.append(ads_code_available[x - 1])
                    else:
                        # Append null
                        ads_code_available.append("")
            elif len(ads_code_available) > ads_space_count:
                ads_code_available = ads_code_available[:ads_space_count]
            else:
                # length is equal
                break
        for ads_code in ads_code_available:
            ads_code = f'<div class="w3-container"><div class="w3-center w3-padding">{ads_code}</div></div>'
            preprocessor_one = re.sub(ads_tag, ads_code, preprocessor_one, 1)
        blog.html_content = preprocessor_one
        return blog  # target.content = preprocessor_one #.format(*ads_code_available)


class BlogView:
    """Endpoints here"""

    @classmethod
    def index(cls):
        """home endpoint"""
        # flash(
        #    "Welcome {}".format("Admin" if current_user.is_authenticated else "user"),
        #    "info",
        # )
        return render_template(
            "blog/index.html",
            blogs=Blog.query.filter_by(is_published=True, link_only=False)
            .order_by(desc(Blog.id))
            .limit(10),
        )

    @classmethod
    def blog_view(cls, uuid):
        """Specific article endpoint"""
        blog = Blog.query.filter_by(uuid=uuid, is_published=True).first_or_404()
        blog.views = blog.views + 1
        db.session.commit()
        related_blogs = (
            Blog.query.filter(
                Blog.categories.any(
                    Category.name.in_([category.name for category in blog.categories])
                )
            )
            .filter(Blog.id != blog.id)
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .order_by(desc(Blog.created_on))
            .limit(10)
            .all()
        )
        return render_template(
            "blog/blog_view.html",
            blog=LocalUtils.add_latest_adverts(blog),
            related_blogs=related_blogs,
            form=CommentForm(
                blog_uuid=uuid,
                email=session.get("comment_user_email"),
                username=session.get("comment_username"),
            )
            or request.cookies.get("user_email"),
        )

    @classmethod
    def category_view(cls, category):
        """Category based view"""

        session["category_query"] = category
        blogs = (
            Blog.query.filter(
                Blog.categories.any(
                    Category.name.in_(
                        [
                            category,
                        ]
                    ),
                ),
            )
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .order_by(desc(Blog.created_on))
            # .limit(10)
            .all()
        )
        total_blogs = len(blogs)
        if total_blogs > 10:
            blogs = blogs[:10]
        if total_blogs:
            if total_blogs == 1:
                session["category_blog_last_id"] = blogs[0].id
            else:
                session["category_blog_last_id"] = blogs[len(blogs) - 1].id
        return render_template(
            "blog/blogs_view.html",
            blogs=blogs,
            total_blogs=total_blogs,
            query=category,
            search_type="category",
        )

    @classmethod
    def load_more_category(cls):
        category = session.get("category_query", "")
        last_viewed_blog_id = session.get("category_blog_last_id", 0)
        blogs = (
            Blog.query.filter(
                Blog.categories.any(
                    Category.name.in_([category]),
                ),
            )
            .filter(Blog.id < last_viewed_blog_id)
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .order_by(desc(Blog.created_on))
            .limit(10)
            .all()
        )  # To be reviewed
        total_blogs = len(blogs)
        if total_blogs:
            session["category_blog_last_id"] = blogs[total_blogs - 1].id
        else:
            return jsonify(is_complete=True)
        return jsonify(
            dict(
                content=render_template(
                    "blog/load_more.html",
                    blogs=blogs,
                ),
                is_complete=False,
            )
        )

    @classmethod
    def search(
        cls,
    ):
        if request.method == "GET":
            """Responds to user while typing"""
            query = request.args.get("q", "")
            blog_titles = (
                Blog.query.filter(
                    or_(
                        Blog.title.like(f"%{query}%"),
                        Blog.content.like(f"%{query}%"),
                        Blog.intro.like(f"%{query}%"),
                        Blog.categories.any(
                            or_(
                                Category.name.like("%query%"),
                                Category.detail.like(f"%{query}%"),
                            ),
                        ),
                    )
                )
                .filter(Blog.is_published == True)
                .filter(Blog.link_only == False)
                .order_by(desc(Blog.created_on))
                .with_entities(Blog.uuid, Blog.title)
                .limit(10)
                .all()
            )
            sorted_titles = []
            for title_list in blog_titles:
                sorted_titles.append(
                    [
                        url_for(
                            "blogs.blog_view",
                            uuid=title_list[0],
                        ),
                        title_list[1],
                    ]
                )
            return jsonify(dict(result=sorted_titles))

        else:
            """Responds to post method searches"""
            query = request.form.get("q", "")
            session["search_query"] = query
            blogs = (
                Blog.query.filter(
                    or_(
                        Blog.title.like(f"%{query}%"),
                        Blog.content.like(f"%{query}%"),
                        Blog.intro.like(f"%{query}%"),
                        Blog.categories.any(
                            or_(
                                Category.name.like("%query%"),
                                Category.detail.like(f"%{query}%"),
                            ),
                        ),
                    )
                )
                .filter(Blog.is_published == True)
                .filter(Blog.link_only == False)
                .order_by(desc(Blog.created_on))
                # .limit(10)
                .all()
            )
            total_blogs = len(blogs)
            if total_blogs > 10:
                blogs = blogs[:10]
            if total_blogs:
                if total_blogs == 1:
                    session["last_blog_id"] = blogs[0].id
                else:
                    session["last_blog_id"] = blogs[len(blogs) - 1].id
            return render_template(
                "blog/blogs_view.html",
                total_blogs=total_blogs,
                blogs=blogs,
                query=query,
                search_type="search",
            )

    @classmethod
    def subscribe(cls):
        email_address = request.form.get("email", "")
        if not email_address:
            return jsonify(dict(message="Enter email address")), 400
        if not re.match(r"\w*\@\w+\.\w+", email_address):
            return jsonify(dict(message="Enter valid email address.")), 400
        if not Subscriber.query.filter_by(email=email_address).first():
            new_subscriber = Subscriber(email=email_address)
            db.session.add(new_subscriber)
            db.session.commit()
            resp = make_response(
                jsonify(dict(message="Check your mail address for confirmation link"))
            )
            resp.set_cookie("user_email", email_address, timedelta(days=180))
            return resp
        else:
            resp = make_response(
                jsonify(dict(message="You've already subscribed!")), 409
            )
            resp.set_cookie("user_email", email_address, timedelta(days=180))
            return resp

    @classmethod
    def comment(cls):
        form = CommentForm()
        uuid = form.blog_uuid.data
        if form.validate_on_submit():
            blog = Blog.query.filter_by(
                uuid=form.blog_uuid.data,
                is_published=True,
                accept_comments=True,
            ).first()
            if blog:
                comment = Comment(
                    username=form.username.data,
                    user_email=form.email.data,
                    content=form.content.data,
                    mood=form.mood.data,
                )
                session["comment_username"] = comment.username
                session["comment_user_email"] = comment.user_email
                blog.comments.append(comment)
                if (
                    len(blog.comments)
                    >= AppDetail.query.filter_by(id=1).first().comments_limit
                ):
                    blog.accept_comments = False

                db.session.commit()
                flash("Comment submitted successfully!", "info")

            else:
                flash(
                    "Blog to be commented on isn't available or doesn't accept comments!",
                    "error",
                )
            return redirect(url_for("blogs.blog_view", uuid=uuid))
        else:
            if uuid:
                flash("Fix errors in the form!", "warn")
                blog = Blog.query.filter_by(uuid=uuid).first_or_404()
                return render_template("blog/blog_view.html", blog=blog, form=form)
            else:
                flash("Malformed form sent!", "error")
                return redirect(url_for("home"))

    @classmethod
    def author(cls, name: str):
        """Filter blogs by author"""
        session["author_query"] = name
        blogs = (
            Blog.query.filter(Blog.authors.any(Admin1.name == name))
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .order_by(desc(Blog.created_on))
            # .limit(10)
            .all()
        )
        total_blogs = len(blogs)
        if total_blogs > 10:
            blogs = blogs[:10]
        if total_blogs:
            if total_blogs == 1:
                session["author_blog_last_id"] = blogs[0].id
            else:
                session["author_blog_last_id"] = blogs[len(blogs) - 1].id
        return render_template(
            "blog/blogs_view.html",
            blogs=blogs,
            total_blogs=total_blogs,
            query=name,
            search_type="author",
        )

    @classmethod
    def load_more_author(cls):
        name = session.get("author_query", "")
        author_blog_last_id = session.get("author_blog_last_id", 0)
        blogs = (
            Blog.query.filter(Blog.authors.any(Admin1.name == name))
            .filter(Blog.id < author_blog_last_id)
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .order_by(desc(Blog.created_on))
            .limit(10)
            .all()
        )
        total_blogs = len(blogs)
        if blogs:
            session["author_blog_last_id"] = blogs[total_blogs - 1].id
        else:
            return jsonify(is_complete=True)
        return jsonify(
            dict(
                content=render_template("blog/load_more.html", blogs=blogs),
                is_complete=False,
            )
        )

    @classmethod
    def confirm_email(cls, token):
        """Verifies susbscriber's email address"""
        subscriber = Subscriber.query.filter_by(token=token).first_or_404()
        subscriber.is_verified = True
        db.session.commit()
        flash("Your subscription is verified successfully", "info")
        return redirect(url_for("home"))

    @classmethod
    def add_like(
        cls,
    ):
        """Adds like count to a blog"""
        uuid = request.args.get("uuid", "")
        if session.get(uuid):
            abort(401)
        blog = Blog.query.filter_by(uuid=uuid, is_published=True).first_or_404()
        blog.likes += 1
        db.session.commit()
        session[uuid] = True
        return jsonify(dict(count=blog.likes))

    @classmethod
    def add_comment_like(
        cls,
    ):
        """Adds like to a comment"""
        id = request.args.get("id", "")
        session_id = "comment-" + id
        if session.get(session_id) or not id.isdigit():
            abort(401)
        comment = Comment.query.filter_by(
            id=str(id),
        ).first_or_404()
        comment.likes += 1
        db.session.commit()
        session[session_id] = True
        return jsonify(dict(count=comment.likes))

    @classmethod
    def load_more_search(
        cls,
    ):
        query = session.get("search_query", "")
        last_blog_id = session.get("last_blog_id", 0)
        blogs = (
            Blog.query.filter(
                or_(
                    Blog.title.like(f"%{query}%"),
                    Blog.content.like(f"%{query}%"),
                    Blog.intro.like(f"%{query}%"),
                    Blog.categories.any(
                        or_(
                            Category.name.like("%query%"),
                            Category.detail.like(f"%{query}%"),
                        ),
                    ),
                )
            )
            .filter(Blog.is_published == True)
            .filter(Blog.link_only == False)
            .filter(Blog.id < last_blog_id)
            .order_by(desc(Blog.created_on))
            .limit(10)
            .all()
        )
        total_blogs = len(blogs)
        if total_blogs:
            session["last_blog_id"] = blogs[total_blogs - 1].id
        else:
            return jsonify(dict(is_complete=True))
        return jsonify(
            dict(
                content=render_template("blog/load_more.html", blogs=blogs),
                is_complete=False,
            )
        )


@app.app_template_global()
def menu_categories():
    """Query Categories from db"""
    return (
        Category.query.filter_by(display_on_menu=True)
        .order_by(Category.display_position)
        .all()
    )


@app.app_template_global()
def trending_blogs():
    """Displays trending blogs"""
    n_days_back = datetime.utcnow() - timedelta(
        days=application.config["TRENDING_SPAN"]
    )
    blogs = (
        Blog.query.filter_by(is_published=True, link_only=False)
        .filter(Blog.created_on >= n_days_back)
        .order_by(desc(Blog.views))
        .limit(8)
        .all()
    )
    return blogs


@app.app_template_global()
def social_media_sites():
    """Displays all social media sites linked"""
    return SocialMedia.query.order_by(SocialMedia.index).all()


@app.app_template_global()
def app_details():
    """Displays appdetails"""
    details = AppDetail.query.filter_by(id=1).first()
    assert details, "Run 'flask user create-admin' before starting server"
    return details


@app.app_template_global()
def weekly_trending_blogs():
    """"""
    seven_days_back = datetime.utcnow() - timedelta(days=7)
    blogs = (
        Blog.query.filter_by(
            is_published=True,
        )
        .filter(Blog.created_on >= seven_days_back)
        .order_by(desc(Blog.views))
        .limit(10)
    )
    return blogs


@app.app_template_global()
def all_time_trending_blogs():
    blogs = Blog.query.filter_by(is_published=True).order_by(desc(Blog.views)).limit(10)
    return blogs


@app.app_template_global()
def advertisement_scripts():
    scripts = Advertisement.query.filter_by(is_script=True, is_active=True).all()
    return scripts


views = BlogView()

app.add_url_rule("/", view_func=views.index, endpoint="index")
app.add_url_rule(
    "/<uuid>",
    view_func=views.blog_view,
    endpoint="blog_view",
)
app.add_url_rule(
    "/category/<category>", view_func=views.category_view, endpoint="category_view"
)
app.add_url_rule(
    "/search", view_func=views.search, endpoint="search", methods=["GET", "POST"]
)
app.add_url_rule(
    "/subscribe", view_func=views.subscribe, endpoint="subscribe", methods=["POST"]
)
app.add_url_rule(
    "/comment", view_func=views.comment, endpoint="comment", methods=["POST"]
)
app.add_url_rule(
    "/author/<name>",
    view_func=views.author,
    endpoint="author",
)
app.add_url_rule(
    "/confirm/<token>", view_func=views.confirm_email, endpoint="confirm_email"
)
app.add_url_rule("/likes", view_func=views.add_like, endpoint="add_like")

app.add_url_rule(
    "/comments-like", view_func=views.add_comment_like, endpoint="add_comment_like"
)

app.add_url_rule(
    "/load-more-search",
    view_func=views.load_more_search,
    endpoint="load_more_search",
    methods=["GET"],
)

app.add_url_rule(
    "/load-more-category",
    view_func=views.load_more_category,
    endpoint="load_more_category",
    methods=["GET"],
)

app.add_url_rule(
    "/load-more-author",
    view_func=views.load_more_author,
    endpoint="load_more_author",
    methods=["GET"],
)
from core.blog.admin import admin

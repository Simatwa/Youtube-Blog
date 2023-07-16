from core.blog import app
from flask import render_template, request, flash, jsonify, make_response, redirect, url_for
from core.blog.models import Blog, Category, Subscriber, SocialMedia, Comment
from core.blog.forms import CommentForm
from sqlalchemy import or_, desc, not_
from core.models import db
from flask_login import login_required
from core.accounts.models import AppDetail

class BlogView:
	"""Enpoints here"""
	
	@classmethod
	def index(cls):
		"""home endpoint"""
		flash("Welcome user","info")
		return render_template("blog/index.html",blogs=Blog.query.filter_by(is_published=True).order_by(desc(Blog.id)).limit(10))
		
	@classmethod
	def blog_view(cls,uuid):
		"""Specific article endpoint"""
		blog = Blog.query.filter_by(uuid=uuid).first_or_404()
		blog.views = blog.views+1
		db.session.commit()
		#related_blogs = Blog.query.filter(Blog.categories.any(Category.name.in_(blog.categories))).filter(_not(Blog.id.any([blog.id]))).limit(10).all()
		related_blogs = Blog.query.filter(Blog.categories.any(Category.name.in_([category.name for category in blog.categories]))).filter(Blog.id != blog.id).limit(10).all()
		#for category in blog.categories:
			#related_blogs.extend(Category.query.filter_by(name=category).first().blogs)
		#related_blogs = Blog.query.filter(or_(**filter_list), not_(Blog.id==blog.id)).all()
		return render_template("blog/blog_view.html",blog=blog, related_blogs=related_blogs, form=CommentForm(blog_uuid=uuid))
		
	@classmethod
	def category_view(cls,category):
		"""Category based view"""
		category = Category.query.filter(Category.name.like(f"%{category}%")).first_or_404()
			
		return render_template("blog/blogs_view.html",blogs=category.blogs, query=category)
		
	@classmethod
	def search(cls,):
		if request.method=="GET":
			"""Responds to user while typing"""
			query = request.args.get('q','')
			blog_titles = Blog.query.filter(or_(Blog.title.like(f'%{query}%'),Blog.content.like(f"%{query}%"), Blog.intro.like(f"%{query}%"), Blog.categories.any(or_(Category.name.like('%query%'),Category.detail.like(f"%{query}%")),),)).order_by(desc(Blog.id)).with_entities(Blog.uuid,Blog.title).limit(10).all()
			sorted_titles = []
			for title_list in blog_titles:
				sorted_titles.append([url_for('blogs.blog_view',uuid=title_list[0],), title_list[1]])
			return jsonify(dict(result=sorted_titles))
			
		else :
			"""Responds to post method searches"""
			query = request.form.get("q",'')
			#blogs = Blog.query.filter(or_(Blog.title.like(query),Blog.content.like(query),Blog.intro.like(query),)).order_by(desc(Blog.id)).all()
			blogs = Blog.query.filter(or_(Blog.title.like(f'%{query}%'),Blog.content.like(f"%{query}%"), Blog.intro.like(f"%{query}%"), Blog.categories.any(or_(Category.name.like('%query%'),Category.detail.like(f"%{query}%")),),)).order_by(desc(Blog.id)).limit(14).all()
			return render_template("blog/blogs_view.html",blogs=blogs, query=query)
	
	@classmethod		
	def subscribe(cls):
		email_address = request.form.get("email","")
		if not email_address:
			return jsonify(dict(message="Enter email address")), 400
		if not Subscriber.query.filter_by(email=email_address).first():
			new_subscriber = Subscriber(email=email_address)
			db.session.add(new_subscriber)
			db.session.commit()
			return jsonify(dict(message="Thank you for subscribing!"))
		else:
			return make_response(jsonify(dict(message="You've already subscribed!")),409)
			
	@classmethod
	def comment(cls):
		form = CommentForm()
		uuid = form.blog_uuid.data
		if form.validate_on_submit():
			blog = Blog.query.filter_by(uuid=form.blog_uuid.data).first()
			if blog:
				comment = Comment(username=form.username.data, user_email=form.email.data, content=form.content.data, mood=form.mood.data)
				blog.comments.append(comment)
				db.session.commit()
				flash("Comment submitted successfully!","info")
				#return redirect(url_for('blogs.view',uuid=uuid))
			else:
				flash("Blog to be commented on isn't available!","error")
			return redirect(url_for('blogs.blog_view',uuid=uuid))
		else:
			if uuid:
				flash("Fix errors in the form!","warn")
				blog = Blog.query.filter_by(uuid=uuid).first_or_404()
				return render_template("blog/blog_view.html",blog=blog,form=form)
			else:
				flash("Malformed form sent!","error")
				return redirect(url_for('home'))
		
@app.app_template_global()
def menu_categories():
	"""Query Categories from db"""
	return Category.query.filter_by(display_on_menu=True).all()
	
@app.app_template_global()
def trending_blogs():
	"""Displays trending blogs"""
	blogs=Blog.query.filter_by(trending=True).order_by(desc(Blog.created_on)).limit(7).all()
	return blogs
	
@app.app_template_global()
def social_media_sites():
	"""Displays all social media sites linked"""
	return SocialMedia.query.all()
	
@app.app_template_global()
def app_details():
	details = AppDetail.query.filter_by(id=1).first()
	assert details, "Enter app details to render blogs"
	return details
	
views = BlogView()

app.add_url_rule("/",view_func=views.index, endpoint="index")
app.add_url_rule("/<uuid>",view_func=views.blog_view, endpoint="blog_view")
app.add_url_rule("/category/<category>",view_func=views.category_view, endpoint="category_view")
app.add_url_rule("/search",view_func=views.search, endpoint="search",methods=["GET","POST"])
app.add_url_rule("/subscribe",view_func=views.subscribe, endpoint="subscribe",methods=["POST"])
app.add_url_rule("/comment",view_func=views.comment, endpoint ="comment",methods=["POST"])
from core.blog.admin import admin
from core.models import db
from core.accounts.models import Admin1
from datetime import datetime
from uuid import uuid4
from os import path, rename, remove
from core.app import application, send_mail
from core.accounts.models import AppDetail
import logging
from slugify import slugify

fullpath = lambda r_path:path.join(application.config["BLOG_IMAGES_DIR"],r_path)
	
class Blog(db.Model):
	__tablename__="blogs"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	author = db.relationship("Admin1",uselist=False, lazy=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text,)
	categories = db.relationship("Category", secondary="blog_category", backref="blogs", lazy=True)
	intro = db.Column(db.Text, nullable=False)
	views = db.Column(db.Integer,default=0)
	likes = db.Column(db.Integer, default=0)
	comments = db.relationship("Comment",backref="blogs", lazy=True)
	uuid = db.Column(db.String(60),nullable=False)
	cover_photo = db.Column(db.String(40),nullable=True,default="default_cover.png")
	image_1 = db.Column(db.String(40), nullable=True)
	image_2 = db.Column(db.String(40), nullable=True)
	image_3 = db.Column(db.String(40), nullable=True)
	image_4 = db.Column(db.String(40), nullable=True)
	link = db.Column(db.String(20), nullable=True)
	trending = db.Column(db.Boolean(), default=False)
	is_published = db.Column(db.Boolean(),default=False)
	is_notified = db.Column(db.Boolean(), default=False)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	lastly_modified = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
	
	def __repr__(self):
		return "<Blog %r>"%self.id
		
	def __str__(self):
		return self.title
		
class Comment(db.Model):
	__tablename__="comments"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(20,), nullable=False,)
	user_email = db.Column(db.String(30),nullable=False)
	content = db.Column(db.Text, nullable=False,)
	mood = db.Column(db.String(10), default='grin')
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	lastly_modified = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
	blog_id = db.Column(db.Integer, db.ForeignKey("blogs.id",onupdate="CASCADE",ondelete="SET NULL"),autoincrement=True)
	
	def __repr__(self):
		return "<Comment %r>"%self.id
		
	def __str__(self):
		return self.username 
	
class Subscriber(db.Model):
	__tablename__="subscribers"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	email = db.Column(db.String(30),nullable=False, unique=True)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	
	def __repr__(self):
		return "<Subscriber %r>"%self.id
		
	def __str__(self):
		return self.email
		
class Category(db.Model):
	__tablename__="categories"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(20), nullable=False)
	detail = db.Column(db.Text,nullable=True)
	icon = db.Column(db.String(15),nullable=True)
	color = db.Column(db.String(15),default="white")
	display_on_menu = db.Column(db.Boolean(),default=True)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	
	def __repr__(self):
		return "<Category %r>"%self.id
	
	def __str__(self):
		return self.name
		
class BlogCategory(db.Model):
	#__tablename__="blogcategories"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	blog_id = db.Column(db.Integer, db.ForeignKey("blogs.id",))
	category_id = db.Column(db.Integer, db.ForeignKey("categories.id",))
	
	def __repr__(self):
		return "<BlogCategory %r>"%self.id

class SocialMedia(db.Model):
	__tablename__ = "socialmedia"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(20), nullable=False)
	link = db.Column(db.String(200), nullable=False)
	color  = db.Column(db.String(15),nullable=False)
	small_screen = db.Column(db.Boolean(), default=False)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	
	def __repr__(self):
		return "<SocialMedia %r>"%self.id
		
	def __init__(self):
		return self.name

class LocalEventListener:
	
	@staticmethod
	def handle_images(mapper, connections, target):
		
		def rename_path(current_path):
			try:
				if len(current_path)==40 or current_path=="default.jpg":
					return 
				new_path = str(uuid4())+current_path[-4:]
				rename(fullpath(current_path),fullpath(new_path))
				return new_path
			except Exception as e:
				logging.error("Failed to rename img {} - {}".format(current_path,e.args))
				
		if target.cover_photo:
			new_name = rename_path(target.cover_photo)
			if new_name:
				target.cover_photo = new_name
		if target.image_1:
			new_name = rename_path(target.image_1)
			if new_name:
				target.image_1 = new_name
				
		if target.image_2:
			new_name = rename_path(target.image_2)
			if new_name:
				target.image_2 =new_name
		
		if target.image_3:
			new_name = rename_path(target.image_3)
			if new_name:
				target.image_3 = new_name
				
		if target.image_4:
			new_name = rename_path(target.image_4)
			if new_name:
				target.image_4 = new_name
				
	@staticmethod
	def delete_images(mapper, connections, target):
		"""Delete blog images"""
		all_images = [target.cover_photo, target.image_1, target.image_2, target.image_3, target.image_4, ]
		for entry in all_images:
			if not entry or entry and entry=="default.jpg":
				continue
			try:
				remove(fullpath(entry))
			except Exception as e:
				logging.error("Failed to delete file -  {}".format(e.args))
	
	@staticmethod
	def generate_uuid(mapper, connections, target):
		"""Generates uuid for each blog"""
		if not ' ' in target.title:
			return
		title = slugify(target.title)
		not_unique = True
		count = 1
		while not_unique:
			if not Blog.query.filter_by(title=title).first():
				target.uuid = title
				not_unique = False
			title = title+'-'+str(count)
			
	@staticmethod
	def mail_blog(mapper, connections, target):
		"""Mails the update to subscribers"""
		if target.is_published:
			if target.is_notified:
				return
		else:
			return 
		appdetail = AppDetail.query.filter_by(id=1).first()
		gen_link = lambda abs_url: appdetail.url+abs_url
		message = f'''
		<h3>{target.title}</h3>
		<img src="{gen_link(url_for('static', filename='images/blog/'+blog.cover_photo))}" max-width="70vh" height="auto" alt="{target.cover_photo}">
		</img>
		<p>{target.intro}</p>
		<p style="text-align:center">To view more of this <a href="{get_link(url_for('blogs.blog_view', uuid=target.uuid))}">click here.</a></p>'''
		subscribers = Subscriber.query.filter_by(is_verified=True).with_entries(Subscriber.email).all()
		if subscribers:
			logging.info(f'Mailing "{target.title}" to {len(subscribers)} subscriber(s)')
			send_mail(subject=target.title, recipients=subscribers, html=message)
		else:
			pass
		
db.event.listen(Blog, "before_insert", LocalEventListener.handle_images)	
db.event.listen(Blog, "before_update", LocalEventListener.handle_images)

db.event.listen(Blog, "before_insert", LocalEventListener.generate_uuid)	
db.event.listen(Blog, "before_update", LocalEventListener.generate_uuid)

db.event.listen(Blog, "before_delete", LocalEventListener.delete_images)			
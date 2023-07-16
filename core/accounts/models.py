from core.models import db
from datetime import datetime
from core.app import bcrypt

class Admin1(db.Model):
	__tablename__="admins"
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(20),nullable=False)
	email = db.Column(db.String(30), nullable=False, unique=True)
	created_on = db.Column(db.DateTime, default=datetime.utcnow)
	password = db.Column(db.String(100),nullable=False)
	password_hashed = db.Column(db.Boolean(),default=True)
	token = db.Column(db.String(10),nullable=True)
	is_admin = db.Column(db.Boolean(), default=False)
	is_authenticated = db.Column(db.Boolean(),default=False)
	is_active = db.Column(db.Boolean(), default=False)
	is_anonymous = db.Column(db.Boolean(), default=True)
	blog_id = db.Column(db.Integer, db.ForeignKey("blogs.id",ondelete="SET NULL", onupdate="CASCADE",name='blog_id'),autoincrement=True)
	appdetail_id =  db.Column(db.Integer, db.ForeignKey("appdetails.id",ondelete="SET NULL", onupdate="CASCADE",name='appdetail_id'),autoincrement=True)
	
	def __repr__(self):
		return "<Admin %r>"%self.id
	
	def __str__(self):
		return self.fname
		
	def get_id(self):
		return self.id
		
	@property
	def fullname(self):
		return self.fname

class AppDetail(db.Model):
	__tablename__="appdetails"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(40), nullable=False)
	description = db.Column(db.Text, nullable=False)
	keywords = db.Column(db.String(500),nullable=False)
	slogan = db.Column(db.String(30), nullable=True)
	owners = db.relationship("Admin1",uselist=True, lazy=True)
	url = db.Column(db.String(50),nullable=False)
	logo = db.Column(db.String(50), default='favicon.png')
	lastly_modified = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
	created_on = db.Column(db.DateTime(), default=datetime.utcnow)
	
	def __repr__(self):
		return "<AppDetail %r>"%self.id
		
	def __str__(self):
		return self.name		

class LocalEventListener:
	"""Listens on Admin1 events"""
	
	@staticmethod
	def hash_password(mapper, connections, target):
		"""Hashes passes"""
		if not target.password_hashed:
			target.password = bcrypt.generate_password_hash(target.password).decode("utf-8")
			target.password_hasshed=True

db.event.listen(Admin1, "before_insert",LocalEventListener.hash_password)
db.event.listen(Admin1, "before_update", LocalEventListener.hash_password)			
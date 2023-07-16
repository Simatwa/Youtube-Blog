from flask import Flask, redirect, url_for
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import login_required
from uuid import uuid4

application = Flask(
    __name__,
    template_folder = "templates",
    static_folder = "static",
    )
  
from dotenv import load_dotenv

load_dotenv(".env")
application.config.from_pyfile("config.py")
  
bcrypt = Bcrypt()
bcrypt.init_app(application)

mail = Mail()
mail.init_app(application)

def generate_uuid():
	return str(uuid4())
	
def send_mail(subject, *args, **kwargs):
	"""Sends mail"""
	try:
		message = Message(subject,*args,**kwargs)
		mail.send(message)
	except Exception as e:
		logging.exception(e)
	
#@login_required
def home():
	return redirect(url_for("blogs.index")) # To be configured
	
@application.template_global()
def enumerate_this(elements):
	return enumerate(elements)

application.add_url_rule("/home",view_func=home, endpoint="home")
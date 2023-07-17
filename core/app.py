from flask import Flask, redirect, url_for, flash, request
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import login_required
from uuid import uuid4
import logging

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
	
@application.errorhandler(400)
def error_400_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(401)
def error_401_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(403)
def error_403_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(404)
def error_404_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(405)
def error_405_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(413)
def error_413_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.errorhandler(429)
def error_429_endpoint(e):
	flash(str(e),"warn")
	return redirect(url_for('home'))
	
@application.template_global()
def enumerate_this(elements):
	return enumerate(elements)

application.add_url_rule("/home",view_func=home, endpoint="home")
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from core.accounts import app
from core.accounts.models import Admin1, AppDetail
from core.models import db
from core.admin import admin
from flask_login import current_user
from flask import abort, redirect, url_for, flash
import click
from wtforms.validators import Email
from flask_login import login_required, current_user
from flask_admin.form import FileUploadField
from flask_wtf.file import FileAllowed
from core.app import application
from flask_admin.contrib.fileadmin import FileAdmin
# from core.app import bcrypt

# from core.app import application
from core.accounts.views import Utils

class FileManagerAdmin(FileAdmin):
    """Manages static files"""
    def __init__(self,*args,**kwargs):
    	super(FileManagerAdmin,self).__init__(*args,**kwargs)
    	can_mkdir = True
    	can_upload = True
    	can_delete = True
    
class AdminModelView(ModelView):
	"""Admin model view"""
	form_base_class = SecureForm
	can_create = True
	can_edit = True
	can_delete = True
	page_size = 50
	can_export = False
	column_display_pk = True
	can_view_details = True
	form_excluded_columns = ["token","created_on", "lastly_modified"]
	column_searchable_list = ["name","email","created_on"]
	column_filters = ["created_on"]
	
	form_args = {
	 "name" : {
	   "label" : "Username",
	     "render_kw" : {
	   "placeholder" : "First, second or both",
	    },
 	 },
 	 
 	 "email": {
 	   "label" : "Email address",
 	   "render_kw" : {
 	     "placeholder" : "example@gmail.com",
 	   },
 	   "validators" : [Email(message="Enter valid email address!")],
 	 },
	}
	
	@login_required
	def is_accessible(self):
		return current_user.is_authenticated
		
	def inaccessible_callback(self, **kwargs):
		flash("You're not authorised to access that site", "danger")
		return redirect(url_for("home"))
		
class AppDetailModelView(ModelView):
	"""Categorya Model view"""
	can_create = True
	can_edit = True
	can_delete = True
	page_size = 50
	can_view_details = True
	column_display_pk = True
	form_excluded_columns = ["lastly_modified","created_on"]
	column_searchable_list = ["name"]
	column_filters = ["created_on"]
	
	form_args = {
	  "name": {
	    "render_kw" : {
	      "placeholder" : "Website name",
	    },
	  },
	  
	  "description" : {
	    "render_kw" : {
	       "placeholder" : "What's this website about?",
	    },
	  },
	  
	  "keywords" : {
	    "render_kw" : {
	      "placeholder" : "Comma separated",
	    },
	  },
	  	  
	  "slogan" : {
	    "render_kw" : {
	      "placeholder" : "Something memorable",
	    },
	  },
	  
	  "url" : {
	    "render_kw" : {
	      "placeholder" : "Link to your website",
	    },
	  },	  
	  	  
	}

	form_extra_fields = {
	  "logo" : 
	    FileUploadField(
	      "Website logo",
	     base_path = application.config["BLOG_IMAGES_DIR"],
	     validators = [
	       FileAllowed(["jpg","png","jpeg"],message="Images only!"),
	     ],
	   ),
	   
	  "cover_photo" : 
	    FileUploadField(
	      "Default blog's cover photo",
	     base_path = application.config["BLOG_IMAGES_DIR"],
	     validators = [
	       FileAllowed(["jpg","png","jpeg"],message="Images only!"),
	     ],
	   ),	   
	}
	
	   		
	@login_required
	def is_accessible(self):
		return current_user.is_authenticated
		
	def inaccessible_callback(self,**kwargs):
		flash("You're not authorised to acess that site")
		return redirect(url_for("home"))

class Cmd:
	
	@staticmethod
	@app.cli.command("create-admin")
	@click.option("--name",help="User name",prompt="User name")
	@click.option("--email",help="User email address", prompt="Email address")
	@click.password_option(prompt="Password")
	def create_admin(name, email, password):
		"""Adds new admin"""
		if Admin1.query.filter_by(email=email).first():
			email = click.prompt(click.style("Email exist, enter new",fg="yellow"))
		new_admin = Admin1(name=name, email=email, password=password, is_admin=True, is_authenticated=True, is_active=True, is_anonymous=False)
		db.session.add(new_admin)
		db.session.commit()
		click.secho("'%s' added as admin successfully"%name, fg="cyan")

admin.add_view(FileManagerAdmin(base_path=application.config["BLOG_IMAGES_DIR"],name="Files"))
admin.add_view(AdminModelView(Admin1, db.session, name="Admins"))
admin.add_view(AppDetailModelView(AppDetail, db.session, name="Website"))

app.cli.add_command(Cmd.create_admin)

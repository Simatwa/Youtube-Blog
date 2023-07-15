from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from core.accounts import app
from core.accounts.models import Admin1
from core.models import db
from core.admin import admin
from flask_login import current_user
from flask import abort, redirect, url_for, flash
import click
from wtforms.validators import Email
from flask_login import login_required, current_user
# from core.app import bcrypt

# from core.app import application
from core.accounts.views import Utils

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
	column_searchable_list = ["fname","email","created_on"]
	column_filters = ["created_on"]
	
	form_args = {
	 "fname" : {
	   "label" : "First name",
	     "render_kw" : {
	   "placeholder" : "Fname",
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
		
class Cmd:
	
	@staticmethod
	@app.cli.command("create-admin")
	@click.option("--fname",help="First name",prompt="First name")
	@click.option("--email",help="User email address", prompt="Email address")
	@click.password_option(prompt="Password")
	def create_admin(fname, email, password):
		"""Adds new admin"""
		if Admin1.query.filter_by(email=email).first():
			email = click.prompt(click.style("Email exist, enter new",fg="yellow"))
		new_admin = Admin1(fname=fname, email=email, password=password, is_admin=True, is_authenticated=True, is_active=True, is_anonymous=False)
		db.session.add(new_admin)
		db.session.commit()
		click.secho("'%s' added as admin successfully"%fname, fg="cyan")

admin.add_view(AdminModelView(Admin1, db.session, name="Admins"))

app.cli.add_command(Cmd.create_admin)

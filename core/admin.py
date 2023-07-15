from flask_admin import Admin
from core.app import application

admin = Admin(application, name="Youtube-Blog", template_mode="bootstrap3")
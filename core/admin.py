from flask_admin import Admin, AdminIndexView
from core.app import application
from flask_login import current_user
from flask import url_for, redirect
from flask_login import login_required

class CustomAdminIndexView(AdminIndexView):
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('accounts.login_user'))

admin = Admin(application, index_view=CustomAdminIndexView(), name=application.config["APP_NAME"], template_mode="bootstrap3")
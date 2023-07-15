from flask_sqlalchemy import SQLAlchemy
from core.app import application

db = SQLAlchemy()
db.init_app(application)
from main import db
from sqlalchemy import func
from sqlalchemy.orm import validates
from flaskext.auth import AuthUser, get_current_user_data
import datetime
from passlib.apps import custom_app_context as pwd_context

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(10))               
    email = db.Column(db.String(80), unique=True)
    spotify_access_token = db.Column(db.String(80))
    spotify_bool = db.Column(db.Boolean)
    soundcloud_bool = db.Column(db.Boolean)
    soundcloud_access_token = db.Column(db.String(80))
    
    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)
from user.models import *
from sqlalchemy import desc, func

def userByLogin(username):
	return User.query.filter(func.lower(User.email) == username).first()
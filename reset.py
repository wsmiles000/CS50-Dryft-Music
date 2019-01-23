#this is used to reset database should it break

from models import *

#drop all tables in database
db.drop_all()

#recreate all tables in database
db.create_all()
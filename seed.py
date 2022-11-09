"""Seed file to make sample data for blogly"""

from models import db, User
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()

# Add user
solomon = User(first_name='Solomon', last_name='Soto')
malachi = User(first_name='Malachi', last_name='Soto')
delilah = User(first_name='Delilah', last_name='Soto')

db.session.add(solomon)
db.session.add(malachi)
db.session.add(delilah)

db.session.commit()

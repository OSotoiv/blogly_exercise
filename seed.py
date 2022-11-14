"""Seed file to make sample data for blogly"""

from models import db, User
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()

# Add user
Mickey = User(first_name='Mickey', last_name='Mouse',
              image_url='https://images.unsplash.com/photo-1667840555698-b859ff73bd13?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')
Donald = User(first_name='Donald', last_name='Duck',
              image_url='https://images.unsplash.com/photo-1667916443896-de20c0ccfc99?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80')
Walt = User(first_name='Walt', last_name='Disney',
            image_url='https://images.unsplash.com/photo-1667802694056-3dd951aba710?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80')

db.session.add(Mickey)
db.session.add(Donald)
db.session.add(Walt)

db.session.commit()

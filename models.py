"""Models for Blogly."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    def __repr__(self):
        return f"""<User
        id={self.id}
        first_name={self.first_name}
        last_name={self.last_name}
        image_url={self.image_url}>"""

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(),
                           nullable=False)
    last_name = db.Column(db.String(),
                          nullable=False)

    image_url = db.Column(db.String())

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    posts = db.relationship('Post')


class Post(db.Model):

    __tablename__ = 'post'

    def __repr__(self):
        return f"< Post >"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')

    @property
    def poster(self):
        print(f"""
        {self.title}
        {self.content}
        {self.created_at}
        {self.user.first_name}""")

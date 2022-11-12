from unittest import TestCase
from models import db, User, Post
from datetime import datetime
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


db.drop_all()
db.create_all()


class Models_test(TestCase):

    @classmethod
    def setUpClass(cls):
        """make Post and User for test"""
        Post.query.delete()
        User.query.delete()
        # create User
        user = User(first_name='Mickey', last_name='Mouse',
                    image_url='fake_img.url')
        # add user to db
        db.session.add(user)
        db.session.commit()
        # after user is submitted add the instance to the cls
        cls.user = user
        id = user.id

        post = Post(title='testing',
                    content='this test should pass', user_id=id)
        db.session.add(post)
        db.session.commit()
        cls.post = post

    # @classmethod
    # def tearDownClass(cls):
        # Post.query.delete()
        # User.query.delete()
        # db.drop_all() this line holds up the test from ending! also holds up the psql db

    def test_users_class(self):
        """test the creation of a User"""
        self.assertIsInstance(self.user, User)
        self.assertEqual(self.user.full_name, 'Mickey Mouse')
        """user and post relationships are connected"""
        self.assertIn(self.post.id, [self.user.posts[0].id])

    def test_posts_class(self):
        """test the creation of a Post"""
        self.assertIsInstance(self.post, Post)
        """user and post relationships are connected"""
        self.assertEqual(self.post.user_id, self.user.id)

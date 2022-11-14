from unittest import TestCase
from models import db, User, Post
from datetime import datetime
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


db.drop_all()
db.create_all()


class App_Routes_Test(TestCase):

    @classmethod
    def setUpClass(cls):
        Post.query.delete()
        User.query.delete()
        # seed db with users
        mickey = User(first_name='Mickey', last_name='Mouse',
                      image_url='https://images.unsplash.com/photo-1667840555698-b859ff73bd13?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80')
        donald = User(first_name='Donald', last_name='Duck',
                      image_url='https://images.unsplash.com/photo-1667916443896-de20c0ccfc99?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80')
        walt = User(first_name='Walt', last_name='Disney',
                    image_url='https://images.unsplash.com/photo-1667802694056-3dd951aba710?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80')
        db.session.add_all([mickey, donald, walt])
        db.session.commit()
        # cls.users = [mickey, donald, walt]
        # cls.ids = [mickey.id, donald.id, walt.id]
        # cls.users = [mickey, donald, walt]

    def setUp(self):
        self.users = User.query.all()
        self.users_tup = db.session.query(
            User.id, User.first_name, User.last_name, User.image_url).all()

    def testDown(self):
        db.session.rollback()

    def test_home(self):
        """testing home route"""
        with app.test_client() as client:
            # test home route for status code and display all users
            res = client.get('/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            # users = User.query.all()
            for user in self.users:
                self.assertIn(
                    f'<li><a href="/user/{user.id}">{user.first_name} {user.last_name}</a></li>', html)

    def test_new_user_form(self):
        """test showing form for new user"""
        with app.test_client() as client:
            res = client.get('/users/new')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('<form action="/users/new" method="POST">', html)
            self.assertIn(
                '<input type="text" class="form-control" id="first_name" name="first_name">', html)
            self.assertIn(
                '<input type="text" class="form-control" id="last_name" name="last_name">', html)
            self.assertIn(
                '<input type="text" class="form-control" id="img_url" name="img_url">', html)

    def test_creat_user_post(self):
        with app.test_client() as client:
            d = {'first_name': 'Dallas', 'last_name': 'Maverick',
                 'img_url': 'test_img.fakeurl'}
            res = client.post('/users/new', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h5 class="card-title">{d["first_name"]} {d["last_name"]}</h5>', html)
            self.assertIn(f'{d["first_name"]} {d["last_name"]}', html)

    def test_user_details(self):
        with app.test_client() as client:
            # users = User.query.all()
            for user in self.users:
                res = client.get(f'/user/{user.id}')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(f'{user.first_name} {user.last_name}', html)

    def test_edit_user_form(self):
        with app.test_client() as client:
            for user in self.users:
                res = client.get(f'/user/{user.id}/edit')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    f'<form class="mb-3" action="/user/{user.id}/edit" method="POST">', html)
                self.assertIn(
                    f'value="{user.first_name}" name="first_name"', html)
                self.assertIn(
                    f'value="{user.last_name}" name="last_name"', html)
                # note: url sent as html has amp entity codes that are not stored on the DB
                # self.assertIn(f'value="{user.image_url}" name="img_url"', html)
                self.assertIn('name="img_url"', html)

    def test_submit_edit_user(self):
        with app.test_client() as client:
            for id, first_name, last_name, image_url in self.users_tup:
                d = {'first_name': first_name+'_edit',
                     'last_name': last_name+'_edit',
                     'img_url': None}
                res = client.post(
                    f'/user/{id}/edit', data=d, follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)

    def test_delete_user(self):
        with app.test_client() as client:
            first_user = User.query.first()
            res = client.get(
                f'/user/{first_user.id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(first_user.first_name, html)
            self.assertNotIn(f'href="/user/{first_user.id}"', html)
            self.assertNotIn(first_user, User.query.all())

    def test_new_post_form(self):
        with app.test_client() as client:
            for user in self.users:
                res = client.get(f'/users/{user.id}/post/new')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    f'action="/users/{user.id}/post/new" method="POST"', html)
                self.assertIn(
                    '<input type="text" class="form-control" id="title" name="title">', html)
                self.assertIn(
                    '<textarea style="height: 100px" class="form-control" id="content" name="content">', html)

    def test_submit_new_post(self):
        with app.test_client() as client:
            for id, first_name, last_name, img in self.users_tup:
                d = {'title': 'this is a test',
                     'content': f'hi my name is {first_name} {last_name}',
                     'user_id': id}
                res = client.post(
                    f'/users/{id}/post/new', data=d, follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(f'{first_name} {last_name}', html)
                self.assertIn(d['title'], html)

    def test_show_post_details(self):
        with app.test_client() as client:
            for user in self.users:
                for post in user.posts:
                    res = client.get(f'/posts/{post.id}')
                    html = res.get_data(as_text=True)
                    self.assertEqual(res.status_code, 200)
                    self.assertIn(post.title, html)
                    self.assertIn(post.content, html)
                    self.assertIn(f'by: {user.first_name}', html)

    def test_edit_post_form(self):
        with app.test_client() as client:
            for user in self.users:
                for post in user.posts:
                    res = client.get(f'/posts/{post.id}/edit')
                    html = res.get_data(as_text=True)
                    self.assertEqual(res.status_code, 'failed!!!!!!!!')

    def test_submit_edit_post(self):
        with app.test_client() as client:
            for user in self.users:
                for post in user.posts:
                    res = client.get('/')
                    html = res.get_data(as_text=True)
                    self.assertEqual(res.status_code, 200)

    def test_delete_post(self):
        with app.test_client() as client:
            res = client.get('/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

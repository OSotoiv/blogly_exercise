from unittest import TestCase
from models import db, User, Post, PostTag, Tag
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

    def setUp(self):

        PostTag.query.delete()
        Tag.query.delete()
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

        fun = Tag(id='fun', name='Funny')
        news = Tag(id='news', name='BreakingNews')
        world = Tag(id='WNews', name='WorldNews')
        health = Tag(id='gut', name='GutHealth')

        db.session.add_all([fun, news, world, health])
        db.session.commit()

        mpost = Post(title='testing 123',
                     content=f'hi my name is {mickey.first_name}', user_id=mickey.id, tags=[health, fun])
        dpost = Post(title='testing 123',
                     content=f'hi my name is {donald.first_name}', user_id=donald.id, tags=[fun, news])
        wpost = Post(title='testing 123',
                     content=f'hi my name is {walt.first_name}', user_id=walt.id, tags=[news, world])
        db.session.add_all([mpost, dpost, wpost])
        db.session.commit()

        # for tag in [health, fun]:
        #     mpost.tags.append(tag)
        # for tag in [fun, news]:
        #     dpost.tags.append(tag)
        # for tag in [news, world]:
        #     wpost.tags.append(tag)
        # db.session.add_all([mpost, dpost, wpost])
        # db.session.commit()

        self.user_post = db.session.query(
            User.id, User.first_name, User.last_name, Post.id, Post.title, Post.content).join(Post).all()
        self.tags = db.session.query(Tag.id, Tag.name).all()
        self.post_tags = db.session.query(
            PostTag.post_id, PostTag.tag_id).all()

    def tearDown(self):
        db.session.rollback()

    def test_home(self):
        """testing home route"""
        with app.test_client() as client:
            # test home route for status code and display all users
            res = client.get('/')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            for userid, first, last, postid, title, content in self.user_post:
                self.assertIn(
                    f'<li><a href="/user/{userid}">{first} {last}</a></li>', html)

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

    def test_creat_new_user(self):
        """test submitting new user form"""
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
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(f'/user/{userid}')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(f'{first} {last}', html)
                self.assertIn(title, html)
                self.assertIn(f'<a href="/posts/{postid}">{title}</a>', html)

    def test_edit_user_form(self):
        """testing getting edit form for user information"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(f'/user/{userid}/edit')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    f'<form class="mb-3" action="/user/{userid}/edit" method="POST">', html)
                self.assertIn(
                    f'value="{first}" name="first_name"', html)
                self.assertIn(
                    f'value="{last}" name="last_name"', html)
                # note: url sent as html has amp entity codes that are not stored on the DB
                # self.assertIn(f'value="{user.image_url}" name="img_url"', html)
                self.assertIn('name="img_url"', html)

    def test_submit_edit_user(self):
        """submitting edited user information"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                d = {'first_name': first+'_edit',
                     'last_name': last+'_edit',
                     'img_url': None}
                res = client.post(
                    f'/user/{userid}/edit', data=d, follow_redirects=True)
                html = res.get_data(as_text=True)
                print(html)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    f'<h5 class="card-title">{first}_edit {last}_edit</h5>', html)
                self.assertIn('<img src="None"', html)

    def test_delete_user(self):
        """test deleting a user"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(
                    f'/user/{userid}/delete', follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertNotIn(first, html)
                self.assertNotIn(f'href="/user/{userid}"', html)
                self.assertFalse(Post.query.filter(
                    Post.user_id == userid).all())
                self.assertFalse(Post.query.filter(Post.id == postid).all())

    def test_new_post_form(self):
        """test getting new post html form"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(f'/users/{userid}/post/new')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    f'action="/users/{userid}/post/new" method="POST"', html)
                self.assertIn(
                    '<input type="text" class="form-control" id="title" name="title">', html)
                self.assertIn(
                    '<textarea style="height: 100px" class="form-control" id="content" name="content">', html)
                for id, name in self.tags:
                    self.assertIn(name, html)
                    self.assertIn(id, html)

    def test_submit_new_post(self):
        """testing submitting a new post form"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                d = {'title': 'this is a test',
                     'content': 'This post is new!',
                     'user_id': userid,
                     'tags': ['news', 'gut']}
                res = client.post(
                    f'/users/{userid}/post/new', data=d, follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(d['title'], html)
                for tag in d['tags']:
                    self.assertIn(tag, html)
                for tag in ['WNews', 'fun']:
                    self.assertNotIn(tag, html)

    def test_show_post_details(self):
        """test for showin post details page"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(f'/posts/{postid}')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(f'<h4 class="card-title">{title}</h4>', html)
                self.assertIn(f'<p class="card-text">{content}</p>', html)

    def test_edit_post_form(self):
        """getting the for for editing a post"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(f'/posts/{postid}/edit')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(f'name="title" value="{title}', html)
                self.assertIn('name="content"', html)
                self.assertIn(content, html)
                self.assertIn(f'action="/posts/{postid}/edit"', html)

    def test_submit_edit_post(self):
        """test submitting a post that has been edited."""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                d = {'title': 'this title has been edited',
                     'content': 'i like python!'}
                res = client.post(
                    f'/posts/{postid}/edit',
                    data=d,
                    follow_redirects=True)

                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(
                    '<h4 class="card-title">this title has been edited</h4>', html)
                self.assertIn('<p class="card-text">i like python!</p>', html)

    def test_delete_post(self):
        """testing deleting a post"""
        with app.test_client() as client:
            for userid, first, last, postid, title, content in self.user_post:
                res = client.get(
                    f'/posts/{postid}/delete', follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)

    def test_show_all_tags(self):
        with app.test_client() as client:
            res = client.get('/tags')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            for id, name in self.tags:
                self.assertIn(id, html)
                self.assertIn(name, html)

    def test_show_tag_details(self):
        with app.test_client() as client:
            for id, name in self.tags:
                res = client.get(f'/tags/{id}')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(id, html)
                self.assertIn(name, html)

    def test_new_tag_form(self):
        with app.test_client() as client:
            res = client.get('/tags/new')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

    def test_make_new_tags(self):
        with app.test_client() as client:
            new_tag = {'tag_id': 'test', 'tag_name': 'test tag'}
            res = client.post('/tags/new',
                              data=new_tag,
                              follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(new_tag['tag_id'], html)
            self.assertIn(new_tag['tag_name'], html)

    def test_edit_tag_form(self):
        with app.test_client() as client:
            for id, name in self.tags:
                res = client.get(f'/tags/{id}/edit')
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(id, html)
                self.assertIn(name, html)

    def test_submit_edited_tag(self):
        with app.test_client() as client:
            for id, name in self.tags:
                new_tag = {'tag_id': id, 'tag_name': 'edited'+name}
                res = client.post(f'/tags/{id}/edit',
                                  data=new_tag,
                                  follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertIn(id, html)
                self.assertIn(new_tag['tag_name'], html)

    def test_delete_tag(self):
        with app.test_client() as client:
            for id, name in self.tags:
                res = client.post(f'/tags/{id}/delete', follow_redirects=True)
                html = res.get_data(as_text=True)
                self.assertEqual(res.status_code, 200)
                self.assertNotIn(id, html)
                self.assertNotIn(name, html)

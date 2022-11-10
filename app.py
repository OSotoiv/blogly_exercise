"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thehouseisyellow'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
connect_db(app)


# db.create_all()


@app.route('/')
def home():
    """show home page"""
    users = User.query.all()
    return render_template('all_users.html', users=users)


@app.route('/users/new')
def new_user_form():
    """route to form to create new user"""
    return render_template('new_user.html')


@app.route('/users/new', methods=["POST"])
def creat_user():
    """route for submitting the new user form"""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    img_url = request.form.get('img_url')
    try:
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=img_url)
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        print('exception raised!')
    flash('welcome!', 'success')
    return redirect(f'/user/{new_user.id}')


@app.route('/user/<int:id>')
def user_details(id):
    user = User.query.get(id)
    posts = user.posts
    return render_template('user_details.html', user=user, posts=posts)


@app.route('/user/<int:id>/edit')
def edit_user_form(id):
    user = User.query.get(id)
    return render_template('edit_user.html', user=user)


@app.route('/user/<int:id>/edit', methods=['POST'])
def submit_edit_user(id):
    user = User.query.get(id)
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.image_url = request.form.get('img_url')
    db.session.add(user)
    db.session.commit()
    return redirect(f'/user/{user.id}')


@app.route('/user/<int:id>/delete')
def delete_user(id):
    User.query.filter(User.id == id).delete()
    db.session.commit()
    return redirect('/')


@app.route('/users/<int:id>/post/new')
def post_form(id):
    return render_template('new_post.html', id=id)


@app.route('/users/<int:id>/post/new', methods=['POST'])
def submit_post(id):
    data = request.form
    post = Post(title=data.get('title'),
                content=data.get('content'),
                user_id=id)
    db.session.add(post)
    db.session.commit()
    return redirect(f'/user/{id}')


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get(post_id)
    user = post.user
    return render_template('post_details.html', post=post, user=user)


@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    post = Post.query.get(post_id)
    return render_template('post_edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def submit_edit_post(post_id):
    post = Post.query.get(post_id)
    post.title = request.form.get('title')
    post.content = request.form.get('content')
    db.session.add(post)
    db.session.commit()
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete')
def delete_post(post_id):
    post = Post.query.get(post_id)
    user = post.user
    Post.query.filter(Post.id == post_id).delete()
    db.session.commit()
    return redirect(f'/user/{user.id}')

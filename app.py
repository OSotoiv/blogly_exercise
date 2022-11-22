"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, PostTag, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thehouseisyellow'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
connect_db(app)


@app.route('/')
def home():
    """show home page with all users"""
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
    for post in Post.query.filter_by(user_id=id).all():
        PostTag.query.filter(PostTag.post_id == post.id).delete()
    db.session.commit()
    Post.query.filter(Post.user_id == id).delete()
    db.session.commit()
    User.query.filter(User.id == id).delete()
    db.session.commit()
    return redirect('/')


@app.route('/users/<int:id>/post/new')
def new_post_form(id):
    tags = db.session.query(Tag.id, Tag.name).all()
    return render_template('new_post.html', id=id, tags=tags)


@app.route('/users/<int:id>/post/new', methods=['POST'])
def submit_new_post(id):
    data = request.form
    tags = Tag.query.filter(Tag.id.in_(data.getlist('tags'))).all()
    post = Post(title=data.get('title'),
                content=data.get('content'),
                user_id=id,
                tags=tags)
    db.session.add(post)
    db.session.commit()
    return redirect(f'/user/{id}')


@app.route('/posts/<int:post_id>')
def show_post_details(post_id):
    post = Post.query.get(post_id)
    user = post.user
    tags = post.tags
    return render_template('post_details.html', post=post, user=user, tags=tags)


@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    all_tags = db.session.query(Tag.id, Tag.name).all()
    post = Post.query.get(post_id)
    post_tags = [tag.id for tag in post.tags]
    return render_template('post_edit.html', post=post, tags=all_tags, post_tags=post_tags)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def submit_edit_post(post_id):
    post = Post.query.get(post_id)
    post.title = request.form.get('title')
    post.content = request.form.get('content')
    post.tags = Tag.query.filter(Tag.id.in_(
        request.form.getlist('tags'))).all()
    db.session.add(post)
    db.session.commit()
    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete')
def delete_post(post_id):
    PostTag.query.filter(PostTag.post_id == post_id).delete()
    db.session.commit()
    post = Post.query.get(post_id)
    id = post.user_id
    Post.query.filter(Post.id == post_id).delete()
    db.session.commit()
    return redirect(f'/user/{id}')


@app.route('/tags')
def show_all_tags():
    tags = db.session.query(Tag.id, Tag.name).all()
    return render_template('allTagsPage.html', tags=tags)


@app.route('/tags/<tagid>')
def show_tag_details(tagid):
    tag = db.session.query(Tag).filter(Tag.id == tagid).first()
    posts = tag.posts
    return render_template('tag_details.html', posts=posts, tag=tag)


@app.route('/tags/new')
def new_tag_form():
    return render_template('newTagForm.html')


@app.route('/tags/new', methods=['POST'])
def make_new_tags():
    id = request.form.get('tag_id')
    name = request.form.get('tag_name')
    tag = Tag(id=id, name=name)
    db.session.add(tag)
    db.session.commit()
    flash('new tag created!')
    return redirect('/tags')


@app.route('/tags/<tagid>/edit')
def edit_tag_form(tagid):
    tag = db.session.query(Tag.id, Tag.name).filter(Tag.id == tagid).first()
    return render_template('editTagForm.html', tag=tag)


@app.route('/tags/<tagid>/edit', methods=['POST'])
def submit_edited_tag(tagid):
    tag = Tag.query.get(tagid)
    tag.id = request.form.get('tag_id')
    tag.name = request.form.get('tag_name')
    db.session.add(tag)
    db.session.commit()
    return redirect('/tags')


@app.route('/tags/<tagid>/delete', methods=['POST'])
def delete_tag(tagid):
    PostTag.query.filter(PostTag.tag_id == tagid).delete()
    db.session.commit()
    Tag.query.filter(Tag.id == tagid).delete()
    db.session.commit()
    flash('Tag has been deleted')
    return redirect('/tags')

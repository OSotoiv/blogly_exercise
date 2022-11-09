"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

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
    return render_template('user_details.html', user=user)


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

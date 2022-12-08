from flask import Flask, request, redirect, url_for, flash, render_template, session, g
from util.helpers import upload_file_to_s3, s3

from werkzeug.utils import secure_filename
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import (
    UserForm, UserEditForm, MessageForm, AddLocationForm, CSRFProtection,
)

from models import (
    db, connect_db, User, Location, DEFAULT_IMAGE_URL)

import os
import sys
import boto3

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]

####################### User Routes ########################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = UserForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


@app.route("/")
def render_form():
    if g.user:
      locations = Location.query.all()
      return render_template("home.html", locations=locations)
    return render_template("base.html")


############################## AWS Routes ################################

# function to check file extension

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def create():
    # breakpoint()
    # check whether an input field with name 'user_file' exist
    if 'user_file' not in request.files:
        flash('No user_file key in request.files')
        return redirect(url_for('new'))

    # after confirm 'user_file' exist, get the file from input
    file = request.files['user_file']

    # check whether a file is selected
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('new'))

    # check whether the file extension is allowed (eg. png,jpeg,jpg,gif)
    if file and allowed_file(file.filename):
        output = upload_file_to_s3(file)

        # if upload success,will return file name of uploaded file
        if output:
            # write your code here
            # to save the file name in database
            sThree = boto3.client('s3')
            result = s3.list_buckets()
            print(result, "<----- result")
            flash("Success upload")
            return redirect("/")

        # upload failed, redirect to upload page
        else:
            flash("Unable to upload, try again")
            return redirect(url_for('new'))

    # if file extension not allowed
    else:
        flash("File type not accepted,please try again.")
        return redirect(url_for('new'))

############################## User Routes ####################################

@app.post('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """
# TODO: change class to Locations as well as route
    db.session.commit()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('show.html', user=user)


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user.

    Redirect to user page on success.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)
    print("Hello Im here----------------------------------------")
    print(user.locations, "<--------- locations")

    # Make an array. Call a function on class User to get list of address
    # When rendering template, pass in array of locations

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('edit.html', form=form, user_id=user.id, user=user)


@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

####################### Location Routes ########################


@app.route('/locations/add', methods=["GET", "POST"])
def add_location():
    """Add new location."""

    form = AddLocationForm()

    user = User.query.filter_by(username=g.user.username).first()
    # print(user1, "<----------- now in user1 in location route")

    # print(request.form, "<--------- form form")

    if form.validate_on_submit():
        try:
            num_price=float(form.price.data)
            location = Location.add(
                owner_id=user.id,
                image_url=form.image_url.data or Location.image_url.default.arg,
                price=num_price,
                details=form.details.data,
                address=form.address.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Invalid information", 'danger')
            return render_template('location/add.html', form=form)

        # print("validated on submit")
        return redirect("/")

    else:
        # breakpoint()
    #     print("sorry not validated")
    # print(form, "<---------- result")
      return render_template('add_locations.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response

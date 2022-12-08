from flask import Flask, request, redirect, flash, render_template, session, g
from util.helpers import upload_file_to_s3

from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

from forms import (
    UserForm, UserEditForm, MessageForm, AddLocationForm, CSRFProtection,
)

from models import (
    db, connect_db, User, Location, Booking)

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
REGION_CODE = os.environ["REGION_CODE"]

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
    
    form = g.csrf_form

    if g.user:
        locations = Location.query.all()
        return render_template("home.html", locations=locations, form=form)
    return render_template("base.html")


############################## AWS Function ################################

""" Takes filename (string). Checks whether file is an allowed file
    Returns boolean
"""
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

############################## User Routes ####################################


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('/users/show.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    """Update/edit profile for current user.

    Redirect to user page on success.
    """

    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)
    print("Hello Im here----------------------------------------")
    print(user.locations, "<--------- locations")

    # Make an array. Call a function on class User to get list of address
    # When rendering template, pass in array of locations FIXME:

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

@app.get('/locations')
def list_users():
    """Page with listing of locations.

    Can take a 'q' param in querystring to search by that username.
    """

    db.session.commit()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        locations = Location.query.all()
    else:
        locations = Location.query.filter(
            Location.address.ilike(f"%{search}%")).all()

    return render_template('home.html', locations=locations)


@app.get('/locations/<int:location_id>')
def show_location(location_id):
    """ Displays location details
        Buttons to book or to go to owner's profile
    """

    location = Location.query.get_or_404(location_id)
    user_id = location.user.id

    return render_template('/locations/show.html', location=location, user_id=user_id)


@app.route('/locations/add', methods=["GET", "POST"])
def add_location():
    """Add new location."""

    form = AddLocationForm()

    user = User.query.filter_by(username=g.user.username).first()

    if form.validate_on_submit():

        # Once user submits, upload the image
        # if there are no errors continue
        file = request.files["image_url"]
        print(file, "<-------------- file")

        if file.filename == '':
            flash("No selected file")
            return redirect('/locations/add')

        if file and allowed_file(file.filename):
            output = upload_file_to_s3(file)
            # print(s3.Bucket(BUCKET_NAME), "<-------- bucket")
            # print(s3.get_object(Bucket=BUCKET_NAME, Key=file.filename), "<------- objects")
            # obj = s3.get_object(Bucket=BUCKET_NAME, Key=file.filename)
            # print(obj['Body'].read().decode("utf-8"), "<========== object get object")
            if output:
                try:
                    img_url = f'https://s3.{REGION_CODE}.amazonaws.com/{BUCKET_NAME}/{file.filename}'
                    location = Location.add(
                        owner_id=user.id,
                        image_url=img_url,  # change to img url from aws
                        price=form.price.data,
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
            return redirect("/locations/add")

    return render_template('add_locations.html', form=form)


@app.post('/locations/<int:location_id>/booked_toggle')
def booked_toggle(location_id):
    """
        Input: location_id
        Output: redirect to root
        Adds or removes record from bookings table and redirects to reference
    """

    form = g.csrf_form

    if not form.validate_on_submit():
        raise Unauthorized

    Booking.toggle_booked(location_id, g.user.id)
    db.session.commit()

    from_url = request.form['from-url']
    return redirect(from_url)


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

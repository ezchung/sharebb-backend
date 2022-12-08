"""SQLAlchemy models for ShareBnB."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://sharebb.s3.us-west-1.amazonaws.com/computer_person.png"


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    locations = db.relationship('Location', backref="user")

    booked_locations = db.relationship(
        'Location',
        secondary='bookings',
        backref='users_who_booked'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Location(db.Model):
    """Location in the system."""

    __tablename__ = 'locations'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default=DEFAULT_IMAGE_URL,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
    )

    details = db.Column(
        db.Text,
        nullable=False,
    )

    @classmethod
    def add(cls, price, image_url, details, owner_id, address):
        """Add new location"""

        location = Location(
            image_url=image_url,
            owner_id=owner_id,
            price=price,
            details=details,
            address=address,
        )

        db.session.add(location)
        return location
    
    def is_booked_by(self,curr_user):
        """ Is this location currently booked by current user? """

        return any(user.id for user in self.users_who_booked if user.id == curr_user.id)


class Booking(db.Model):
    """ Bookings in the system """

    __tablename__ = 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    location_id = db.Column(
        db.Integer,
        db.ForeignKey('locations.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    __table_args__ = (db.UniqueConstraint(location_id, user_id),)

    @classmethod
    def toggle_booked(cls, location_id, user_id):
        """ Is the location booked by current user?
            Add or remove record from bookings table
        """

        booked = cls.query.filter(
            (user_id == cls.user_id) &
            (location_id == cls.location_id)
        ).one_or_none()

        if not booked:
            new_booking = cls(location_id=location_id, user_id=user_id)

            db.session.add(new_booking)
        else:
            db.session.delete(booked)


def connect_db(app):
    """Connect this database to provided Flask app."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

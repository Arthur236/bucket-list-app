from app import db
from flask_bcrypt import Bcrypt
from slugify import slugify
from sqlalchemy import event


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    slug = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    bucket_lists = db.relationship(
        'BucketList', order_by='BucketList.id', cascade="all, delete-orphan")

    def __init__(self, username, email, password):
        """Initialize the user with an email and a password."""
        self.username = username
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()


class BucketList(db.Model):
    """This class represents the bucket_list table."""

    __tablename__ = 'bucket_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    slug = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, user_id, name, description):
        """initialize with name."""
        self.user_id = user_id
        self.name = name
        self.description = description

    @staticmethod
    def slugify(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return BucketList.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucket list: {}>".format(self.name)


# Set slug value during create and update events
event.listen(User.username, 'set', User.slugify, retval=False)
event.listen(BucketList.name, 'set', BucketList.slugify, retval=False)

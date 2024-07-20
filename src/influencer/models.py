from datetime import datetime
from flask_login import UserMixin
from src import bcrypt, db


class Influencer(UserMixin, db.Model): #UserMixin is a class that includes default implementations for the methods that Flask-Login expects user objects to have

    __tablename__ = "influencers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String, nullable=False, default="influencer")
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    instagram_handle = db.Column(db.String, nullable=True)
    instagram_followers = db.Column(db.Integer, nullable=True)
    x_handle = db.Column(db.String, nullable=True)
    x_followers = db.Column(db.Integer, nullable=True)
    youtube_handle = db.Column(db.String, nullable=True)
    youtube_subscribers = db.Column(db.Integer, nullable=True)
    facebook_handle = db.Column(db.String, nullable=True)
    facebook_followers = db.Column(db.Integer, nullable=True)

    def __init__(self, email, password, name, category, niche, instagram_handle, instagram_followers, x_handle, x_followers, youtube_handle, youtube_subscribers, facebook_handle, facebook_followers):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.role = "influencer"
        self.name = name
        self.category = category
        self.niche = niche
        self.instagram_handle = instagram_handle
        self.instagram_followers = instagram_followers
        self.x_handle = x_handle
        self.x_followers = x_followers
        self.youtube_handle = youtube_handle
        self.youtube_subscribers = youtube_subscribers
        self.facebook_handle = facebook_handle
        self.facebook_followers = facebook_followers

    def __repr__(self):
        return f"<email {self.email}>"
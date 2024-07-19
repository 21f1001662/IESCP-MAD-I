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

    def __init__(self, email, password, name, category, niche):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.role = "influencer"
        self.name = name
        self.category = category
        self.niche = niche

    def __repr__(self):
        return f"<email {self.email}>"
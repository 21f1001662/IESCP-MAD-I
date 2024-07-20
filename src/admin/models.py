from datetime import datetime
from flask_login import UserMixin
from src import bcrypt, db


class Admin(UserMixin, db.Model): #UserMixin is a class that includes default implementations for the methods that Flask-Login expects user objects to have

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String, nullable=False, default="admin")

    def __init__(self, email, password, role="admin"):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf8')
        self.created_on = datetime.now()
        self.role = role

    def __repr__(self):
        return f"<email {self.email}>"
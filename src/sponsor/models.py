from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Enum
import enum
from src import bcrypt, db

class VisibilityEnum(enum.Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"

class Sponsor(UserMixin, db.Model): #UserMixin is a class that includes default implementations for the methods that Flask-Login expects user objects to have
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String, nullable=False, default="sponsor")
    name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)

    def __init__(self, email, password, name, industry, budget):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf8')
        self.created_on = datetime.now()
        self.role = "sponsor"
        self.name = name
        self.industry = industry
        self.budget = budget

    def __repr__(self):
        return f"<email {self.email}>"
    
class Campaigns(UserMixin, db.Model): #UserMixin is a class that includes default implementations for the methods that Flask-Login expects user objects to have
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(Enum(VisibilityEnum), nullable=False)
    goals = db.Column(db.String, nullable=False)

    def __init__(self, name, description, start_date, end_date, budget, visibility, goals):
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.visibility = visibility
        self.goals = goals

    def __repr__(self):
        return f"<email {self.email}>"
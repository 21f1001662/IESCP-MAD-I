from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Enum
import enum
from src import bcrypt, db

class MessageVisibilityEnum(enum.Enum):
    SENT = "Sent"
    SEEN = "Seen"

class AdRequestStatusEnum(enum.Enum):
    Pending = "Pending"
    Seen = "Seen"
    Accepted = "Accepted"
    Rejected = "Rejected"

class Message(UserMixin, db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)
    ad_request = db.Column(db.Integer, db.ForeignKey('ad_requests.id'))
    sender_name = db.Column(db.String, nullable=False)
    message_visibility = db.Column(Enum(MessageVisibilityEnum), nullable=False)
    sent_time = db.Column(db.DateTime, nullable=False)
    seen_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, message, ad_request, sender_name, sent_time=None):
        self.message = message
        self.ad_request = ad_request
        self.sender_name = sender_name
        self.sent_time = sent_time or datetime.now()
        self.message_visibility = MessageVisibilityEnum.SENT
    
    def __repr__(self):
        return f"<id {self.id} | {self.message}>"

class AdRequest(UserMixin, db.Model):
    __tablename__ = "ad_requests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    status = db.Column(Enum(AdRequestStatusEnum), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    campaign = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    sponsor = db.Column(db.Integer, db.ForeignKey('sponsors.id'))
    influencer = db.Column(db.Integer, db.ForeignKey('influencers.id'))
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, budget, campaign, sponsor, influencer):
        self.name = name
        self.status = AdRequestStatusEnum.Pending
        self.budget = budget
        self.campaign = campaign
        self.sponsor = sponsor
        self.influencer = influencer
        self.created_at = datetime.now()
        
    def __repr__(self):
        return f"<id {self.id} | {self.name}>"
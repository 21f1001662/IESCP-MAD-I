from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional
from src.influencer.models import Influencer

class InfluencerLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class InfluencerRegisterForm(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(), Email(message=None), Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    name = StringField("Name", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    niche = StringField("Niche", validators=[DataRequired()])
    instagram_handle = StringField("Instagram Handle", validators=[Optional(), URL()])
    instagram_followers = IntegerField("Instagram Followers", validators=[Optional()])
    x_handle = StringField("X Handle", validators=[Optional(), URL()])
    x_followers = IntegerField("X Followers", validators=[Optional()])
    youtube_handle = StringField("YouTube Handle", validators=[Optional(), URL()])
    youtube_subscribers = IntegerField("YouTube Subscribers", validators=[Optional()])
    facebook_handle = StringField("Facebook Handle", validators=[Optional(), URL()])
    facebook_followers = IntegerField("Facebook Followers", validators=[Optional()])

    def validate(self, extra_validators=None):
        initial_validation = super(InfluencerRegisterForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        influencer = Influencer.query.filter_by(email=self.email.data).first()
        if influencer:
            self.email.errors.append("influencer Email already registered")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        return True
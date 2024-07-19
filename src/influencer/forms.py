from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length
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
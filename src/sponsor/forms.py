from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from src.sponsor.models import Sponsor, VisibilityEnum

class SponsorLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class SponsorRegisterForm(FlaskForm):
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
    industry = StringField("Industry", validators=[DataRequired()])
    budget = IntegerField("Budget", validators=[DataRequired()])
    

    def validate(self, extra_validators=None):
        initial_validation = super(SponsorRegisterForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        sponsor = Sponsor.query.filter_by(email=self.email.data).first()
        if sponsor:
            self.email.errors.append("Sponsor Email already registered")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        return True

class CreateCampaignForm(FlaskForm):
    id = IntegerField("ID", validators=[Optional()])
    name = StringField("Campaign Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    start_date = StringField("Start Date", validators=[DataRequired()])
    end_date = StringField("End Date", validators=[DataRequired()])
    budget = IntegerField("Budget", validators=[DataRequired()])
    visibility = SelectField("Visibility", choices=[(visibility.name, visibility.value) for visibility in VisibilityEnum], validators=[DataRequired()])
    goals = TextAreaField("Goals", validators=[DataRequired()])
    
class InfluencerSearchForm(FlaskForm):
    name = StringField("Name", validators=[Optional()])
    category = StringField("Category", validators=[Optional()])
    
class AdRequestForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    budget = IntegerField("Budget", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    campaign = IntegerField("Campaign", validators=[DataRequired(message="Campaign is required")])
    
    def validate(self, extra_validators=None):
        initial_validation = super(AdRequestForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        if self.budget.data <= 0:
            self.budget.errors.append("Budget must be greater than 0")
            return False
        return True
    
class AdRequestUpdateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    budget = IntegerField("Budget", validators=[DataRequired()])
    campaign = IntegerField("Campaign", validators=[DataRequired(message="Campaign is required")])
    
    def validate(self, extra_validators=None):
        initial_validation = super(AdRequestUpdateForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        if self.budget.data <= 0:
            self.budget.errors.append("Budget must be greater than 0")
            return False
        return True
    
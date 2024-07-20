from flask import session, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from .forms import SponsorLoginForm, SponsorRegisterForm, CreateCampaignForm

from src import bcrypt, db
from src.sponsor.models import Sponsor, Campaigns

sponsor_bp = Blueprint("sponsor", __name__)

@sponsor_bp.route("/dashboard")
def dashboard():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        return render_template("sponsor/dashboard.html", request=request)
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/campaigns")
def campaigns():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        # fetch all campaigns created by the sponsor
        campaigns = Campaigns.query.filter_by(created_by=current_user.id).all()
        return render_template("sponsor/campaigns.html", campaigns=campaigns)
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/campaigns/add", methods=["GET", "POST"])
def add_campaigns():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        form = CreateCampaignForm(request.form)
        if form.validate_on_submit():
            campaign = Campaigns(
                name=form.name.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                budget=form.budget.data,
                visibility=form.visibility.data,
                goals=form.goals.data,
                created_by=current_user.id
            )
            db.session.add(campaign)
            db.session.commit()            
            flash("Campaign added successfully.", "success")
            return redirect(url_for("sponsor.campaigns"))        
        return render_template("sponsor/add_campaigns.html", form=form)
    return redirect(url_for("sponsor.login"))
    
@sponsor_bp.route("/stats")
def stats():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        return render_template("sponsor/stats.html")
    else:
        return redirect(url_for("sponsor.stats"))
    
@sponsor_bp.route("/find")
def find():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        return render_template("sponsor/find.html")
    else:
        return redirect(url_for("sponsor.find"))

@sponsor_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        flash("You are already registered.", "info")
        return redirect(url_for("sponsor.dashboard"))
    form = SponsorRegisterForm(request.form)
    if form.validate_on_submit():
        sponsor = Sponsor(
            email=form.email.data, 
            password=form.password.data,
            name=form.name.data,
            industry=form.industry.data,
            budget=form.budget.data
        )
        db.session.add(sponsor)
        db.session.commit() 
        
        session["role"] = "sponsor"  # add role to session
        login_user(sponsor)
        flash("You registered and are now logged in. Welcome!", "success")
        
        return redirect(url_for("sponsor.dashboard"))
    
    return render_template("sponsor/register.html", form=form)

@sponsor_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        flash("You are already registered.", "info")
        return redirect(url_for("sponsor.dashboard"))
    
    form = SponsorLoginForm(request.form)
    
    if form.validate_on_submit():
        user = Sponsor.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            session["role"] = "sponsor"  # add role to session
            login_user(user)           
            return redirect(url_for("sponsor.dashboard"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("sponsor/login.html", form=form)

    
    # This is for handling a GET request
    return render_template("sponsor/login.html", form=form)

@sponsor_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("core.home"))



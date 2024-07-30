from flask import session, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from .forms import InfluencerLoginForm, InfluencerRegisterForm

from src import bcrypt, db
from src.influencer.models import Influencer

influencer_bp = Blueprint("influencer", __name__)

@influencer_bp.route("/dashboard")
def dashboard():
    if current_user.is_authenticated and session.get("role") == "influencer":
        return render_template("influencer/dashboard.html")
    else:
        return redirect(url_for("influencer.login"))
    
@influencer_bp.route("/requests")
def requests():
    if current_user.is_authenticated and session.get("role") == "influencer":
        return render_template("influencer/requests.html")
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/find")
def find():
    if current_user.is_authenticated and session.get("role") == "influencer":
        return render_template("influencer/find.html")
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/stats")
def stats():
    if current_user.is_authenticated and session.get("role") == "influencer":
        return render_template("influencer/stats.html")
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and session.get("role") == "influencer":
        flash("You are already registered.", "info")
        return redirect(url_for("influencer.dashboard"))
    form = InfluencerRegisterForm(request.form)
    if form.validate_on_submit():
        print("form validated")
        influencer = Influencer(
            email=form.email.data, 
            password=form.password.data,
            name=form.name.data,
            category=form.category.data,
            niche=form.niche.data,
            x_handle=form.x_handle.data,
            x_followers=form.x_followers.data,
            youtube_handle=form.youtube_handle.data,
            youtube_subscribers=form.youtube_subscribers.data,
            facebook_handle=form.facebook_handle.data,
            facebook_followers=form.facebook_followers.data,
            instagram_handle=form.instagram_handle.data,
            instagram_followers=form.instagram_followers.data,
        )
        db.session.add(influencer)
        db.session.commit() 
        
        session["role"] = "influencer"  # add role to session
        login_user(influencer)
        flash("You registered and are now logged in. Welcome!", "success")
        
        return redirect(url_for("influencer.dashboard"))
    
    return render_template("influencer/register.html", form=form)

@influencer_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and session.get("role") == "influencer":
        flash("You are already registered.", "info")
        return redirect(url_for("influencer.dashboard"))
    
    form = InfluencerLoginForm(request.form)
    
    if form.validate_on_submit():
        user = Influencer.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            session["role"] = "influencer"  # add role to session
            login_user(user)           
            return redirect(url_for("influencer.dashboard"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("influencer/login.html", form=form)

    
    # This is for handling a GET request
    return render_template("influencer/login.html", form=form)

@influencer_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("core.home"))



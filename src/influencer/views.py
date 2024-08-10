from flask import session, Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, current_user, login_required
from .forms import InfluencerLoginForm, InfluencerRegisterForm, CampaignSearchForm, AdRequestForm, AdRequestUpdateForm, AdRequestResponseForm
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime, timedelta
from sqlalchemy import func

from src import bcrypt, db
from src.influencer.models import Influencer
from src.sponsor.models import Campaigns, Sponsor
from src.core.models import AdRequest, AdRequestStatusEnum, AdRequestSenderEnum, Message

influencer_bp = Blueprint("influencer", __name__)

@influencer_bp.route("/dashboard")
def dashboard():
    if current_user.is_authenticated and session.get("role") == "influencer":
        influencer = Influencer.query.get(current_user.id)
        new_ad_requests = db.session.query(AdRequest, Campaigns, Sponsor)\
            .join(Campaigns, AdRequest.campaign == Campaigns.id)\
            .join(Sponsor, AdRequest.sponsor == Sponsor.id)\
            .filter(AdRequest.influencer == influencer.id, AdRequest.sender == AdRequestSenderEnum.Sponsor, AdRequest.status == AdRequestStatusEnum.Pending).all()
        active_ad_requests = db.session.query(AdRequest, Campaigns, Sponsor)\
            .join(Campaigns, AdRequest.campaign == Campaigns.id)\
            .join(Sponsor, AdRequest.sponsor == Sponsor.id)\
            .filter(AdRequest.influencer == influencer.id, AdRequest.status == AdRequestStatusEnum.Accepted).all()
        return render_template("influencer/dashboard.html", new_ad_requests=new_ad_requests, active_ad_requests=active_ad_requests, influencer=influencer, AdRequestStatusEnum=AdRequestStatusEnum, AdRequestSenderEnum=AdRequestSenderEnum)
    else:
        return redirect(url_for("influencer.login"))
    
@influencer_bp.route("/requests")
def requests():
    if current_user.is_authenticated and session.get("role") == "influencer":
        influencer = Influencer.query.get(current_user.id)
        ad_requests = db.session.query(AdRequest, Campaigns, Sponsor)\
            .join(Campaigns, AdRequest.campaign == Campaigns.id)\
            .join(Sponsor, AdRequest.sponsor == Sponsor.id)\
            .filter(AdRequest.influencer == influencer.id).all()
        
        return render_template("influencer/requests.html", influencer=influencer, ad_requests=ad_requests, AdRequestStatusEnum=AdRequestStatusEnum)
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/ad_request/<int:ad_request_id>/send_message", methods=["POST"])
def send_message(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "influencer":
        ad_request_id = request.view_args["ad_request_id"]
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        if ad_request.influencer != current_user.id:
            flash("You are not authorized to send a message for this ad request.", "danger")
            return redirect(url_for("influencer.requests"))
        
        form = AdRequestUpdateForm(request.form)
        message = Message(
            message=form.message.data,
            ad_request=ad_request_id,
            sender_name=current_user.name
        )
        db.session.add(message)
        db.session.commit()
        flash("Message sent successfully.", "success")
        return redirect(url_for("influencer.ad_request", ad_request_id=ad_request_id))
    else:
        return redirect(url_for("influencer.login"))  
  
@influencer_bp.route("/ad_request/<int:ad_request_id>", methods=['GET', 'POST'])
def ad_request(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "influencer":
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        
        if ad_request is None:
            flash("Ad request not found!", "danger")
            return redirect(url_for("influencer.requests"))
        
        if (ad_request.influencer != current_user.id):
            flash("You do not have permission to view this ad request.", "danger")
            return redirect(url_for("influencer.requests"))
        
        form = AdRequestUpdateForm(request.form)
        if form.validate_on_submit():
            ad_request.name = form.name.data
            ad_request.budget = form.budget.data
            ad_request.message = form.message.data
            db.session.commit()
            flash("Ad request updated successfully.", "success")
            return redirect(url_for("influencer.ad_request", ad_request_id=ad_request_id))
        
        influencer = Influencer.query.filter_by(id = current_user.id).first()
        campaign = Campaigns.query.filter_by(id = ad_request.campaign).first()
        messages = Message.query.filter_by(ad_request = ad_request_id )
        
        form.name.data = ad_request.name
        form.budget.data = ad_request.budget
        form.campaign.data = ad_request.campaign
        
        return render_template("influencer/ad_request.html", form=form, ad_request=ad_request, influencer=influencer, messages=messages, campaign=campaign, AdRequestStatusEnum=AdRequestStatusEnum, AdRequestSenderEnum=AdRequestSenderEnum)
    else:
        return redirect(url_for("influencer.login"))
    
@influencer_bp.route("/ad_request/create/<int:campaign_id>", methods=["GET", "POST"])
def create_ad_request(campaign_id):
    if current_user.is_authenticated and session.get("role") == "influencer":
        form = AdRequestForm(request.form)
        campaign_id = request.view_args["campaign_id"]
        campaign = Campaigns.query.get(campaign_id)
        if form.validate_on_submit():
            ad_request = AdRequest(
                name=form.name.data,
                budget=form.budget.data,
                campaign=form.campaign.data,
                sponsor=campaign.created_by,
                influencer=current_user.id,
                sender=AdRequestSenderEnum.Influencer
            )
            db.session.add(ad_request)
            db.session.commit()
            flash("Ad request created successfully.", "success")
            return redirect(url_for("influencer.requests"))
        return render_template("influencer/ad_request_form.html", campaign=campaign, campaign_id = campaign_id, form=form)
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/ad_request/response", methods=["POST"])
def respond_to_ad_request():
    if current_user.is_authenticated and session.get("role") == "influencer":
        form = AdRequestResponseForm(request.form)
        if form.validate_on_submit():
            ad_request = AdRequest.query.filter_by(id=form.ad_request_id.data).first()
            if ad_request.influencer != current_user.id:
                flash("You are not authorized to respond to this ad request.", "danger")
                return redirect(url_for("influencer.requests"))
            
            ad_request.status = form.response.data
            db.session.commit()
            flash(f"Ad request {ad_request.status.value} successfully.", "success")
            return redirect(url_for("influencer.ad_request", ad_request_id=ad_request.id))
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/find", methods=["GET", "POST"])
def find():
    if current_user.is_authenticated and session.get("role") == "influencer":
        form = CampaignSearchForm(request.form)
        if form.validate_on_submit():
            name_search_term = f"%{form.name.data}%"
            budget_search_term = form.budget.data if form.budget.data else 0
            campaigns = db.session.query(Campaigns, Sponsor).join(Sponsor, Campaigns.created_by == Sponsor.id).filter(Campaigns.name.ilike(name_search_term), Campaigns.budget >= budget_search_term).all()
            return render_template("influencer/find.html", campaigns= campaigns, form=form)
        
        campaigns = db.session.query(Campaigns, Sponsor).join(Sponsor, Campaigns.created_by == Sponsor.id).all()
        return render_template("influencer/find.html", campaigns= campaigns, form=form)
    else:
        return redirect(url_for("influencer.login"))

@influencer_bp.route("/stats")
def stats():
    if current_user.is_authenticated and session.get("role") == "influencer":
        
        stats = {}
        ad_requests_count = AdRequest.query.count()
        stats['ad_requests_count'] = ad_requests_count
        
        accepted_request_count = AdRequest.query.filter_by(influencer = current_user.id, status=AdRequestStatusEnum.Accepted).count()
        rejected_request_count = AdRequest.query.filter_by(influencer = current_user.id, status=AdRequestStatusEnum.Rejected).count()
        completed_request_count = AdRequest.query.filter_by(influencer = current_user.id, status=AdRequestStatusEnum.Completed).count()
        pending_request_count = AdRequest.query.filter_by(status=AdRequestStatusEnum.Pending).count()
        stats['ad_request_stats'] = [accepted_request_count, rejected_request_count, completed_request_count, pending_request_count]
        
        # return daily ad_requests groupby day sort ascending by date
        daily_ad_requests = db.session.query(func.count(AdRequest.id), func.date(AdRequest.created_at)).filter(AdRequest.influencer == current_user.id).group_by(func.date(AdRequest.created_at)).order_by(func.date(AdRequest.created_at)).all()
        lables = []
        values = []
        cumulative = 0
        # fill missing dates from the first date to the last date
        if daily_ad_requests:
            first_date = datetime.strptime(daily_ad_requests[0][1], '%Y-%m-%d')
            last_date = datetime.strptime(daily_ad_requests[-1][1], '%Y-%m-%d')
            date = first_date
            while date <= last_date:
                lables.append(date.strftime('%Y-%m-%d'))
                for ad_request in daily_ad_requests:
                    if ad_request[1] == date:
                        cumulative += ad_request[0]
                        values.append(cumulative)
                        break
                else:
                    values.append(cumulative)
                date += timedelta(days=1)
        
        stats['daily_ad_requests'] = {'labels': lables, 'values': values}

        return render_template("influencer/stats.html", stats=stats)
    else:
        return redirect(url_for("influencer.login"))


@influencer_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and session.get("role") == "influencer":
        flash("You are already registered.", "info")
        return redirect(url_for("influencer.dashboard"))
    form = InfluencerRegisterForm(request.form)
    if form.validate_on_submit():
        # Handle file upload
        image_file = request.files.get("image")
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            filename = f"{int(time.time())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(upload_path)
        influencer = Influencer(
            email=form.email.data, 
            password=form.password.data,
            name=form.name.data,
            about=form.about.data,
            image=filename,
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



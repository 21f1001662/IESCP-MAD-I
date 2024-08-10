from flask import session, Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, current_user, login_required
from .forms import SponsorLoginForm, SponsorRegisterForm, CreateCampaignForm, InfluencerSearchForm, AdRequestForm, AdRequestUpdateForm, AdRequestResponseForm
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime, timedelta
from sqlalchemy import func

from src import bcrypt, db
from src.sponsor.models import Sponsor, Campaigns
from src.influencer.models import Influencer
from src.core.models import Message, AdRequest, AdRequestStatusEnum, AdRequestSenderEnum

sponsor_bp = Blueprint("sponsor", __name__)

@sponsor_bp.route("/dashboard")
def dashboard():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        campaigns = Campaigns.query.filter_by(created_by=current_user.id).all()[:5]
        sponsor = Sponsor.query.filter_by(id=current_user.id).first()
        ad_requests = db.session.query(AdRequest, Sponsor, Influencer).\
            join(Sponsor, AdRequest.sponsor == Sponsor.id).\
            join(Influencer, AdRequest.influencer == Influencer.id).\
            filter(AdRequest.sponsor == sponsor.id, AdRequest.sender == AdRequestSenderEnum.Influencer, AdRequest.status == AdRequestStatusEnum.Pending).all()
        
        return render_template("sponsor/dashboard.html", campaigns=campaigns, ad_requests=ad_requests, sponsor=sponsor, AdRequestStatusEnum=AdRequestStatusEnum)
    
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
    
@sponsor_bp.route("/campaigns/<int:campaign_id>", methods=["GET"])
def campaign_details(campaign_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        campaign_id = request.view_args["campaign_id"]
        campaign_data = Campaigns.query.filter_by(id=campaign_id).first()
        
        ad_requests = db.session.query(AdRequest, Sponsor, Influencer).\
            join(Sponsor, AdRequest.sponsor == Sponsor.id).\
            join(Influencer, AdRequest.influencer == Influencer.id).\
            filter(AdRequest.campaign == campaign_id).all()
        
        return render_template("sponsor/campaign_details.html", campaign=campaign_data, ad_requests=ad_requests, AdRequestStatusEnum=AdRequestStatusEnum)
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
        return render_template("sponsor/campaigns_form.html", form=form, purpose="POST")
    return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/campaigns/edit/<int:campaign_id>", methods=["GET", "POST"])
def edit_campaigns(campaign_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        campaign_id = request.view_args["campaign_id"]
        form = CreateCampaignForm(request.form)
        if form.validate_on_submit():
            form = CreateCampaignForm(request.form)
            campaign = Campaigns.query.filter_by(id=campaign_id).first()
            
            if campaign.created_by != current_user.id:
                flash("You are not authorized to edit this campaign.", "danger")
                return redirect(url_for("sponsor.campaigns"))
            
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.start_date = form.start_date.data
            campaign.end_date = form.end_date.data
            campaign.budget = form.budget.data
            campaign.visibility = form.visibility.data
            campaign.goals = form.goals.data
            db.session.commit()
            flash("Campaign updated successfully.", "success")
            return redirect(url_for("sponsor.campaigns"))
        else:
            campaign_data = Campaigns.query.filter_by(id=campaign_id).first()
            form = CreateCampaignForm(obj = campaign_data)
            return render_template("sponsor/campaigns_form.html", form=form, purpose="PATCH")
    return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/find", methods=["POST", "GET"])
def find_influencers():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        form = InfluencerSearchForm(request.form)
        campaign_id = request.args.get("campaign_id")
        if form.validate_on_submit():
            search_term = f"%{form.name.data}%"
            category_term = f"%{form.category.data}%"
            influencers = Influencer.query.filter(
                Influencer.name.like(search_term),
                Influencer.category.like(category_term)
            ).all()
            return render_template("sponsor/find.html", form=form, influencers=influencers)
        
        influencers = Influencer.query.all()
        return render_template("sponsor/find.html", form=form, influencers=influencers, campaign_id=campaign_id)
    else:
        return redirect(url_for("sponsor.find"))

@sponsor_bp.route("/campaigns/delete/<int:campaign_id>", methods=["POST"])
def delete_campaigns(campaign_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        campaign_id = request.view_args["campaign_id"]
        campaign = Campaigns.query.filter_by(id=campaign_id).first()
        if campaign.created_by != current_user.id:
            flash("You are not authorized to delete this campaign.", "danger")
            return redirect(url_for("sponsor.campaigns"))
        db.session.delete(campaign)
        db.session.commit()
        flash("Campaign deleted successfully.", "success")
        return redirect(url_for("sponsor.campaigns"))
    return redirect(url_for("sponsor.login"))
    
@sponsor_bp.route("/stats")
def stats():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        
        stats = {}
        ad_requests_count = AdRequest.query.count()
        stats['ad_requests_count'] = ad_requests_count
        
        accepted_request_count = AdRequest.query.filter_by(sponsor = current_user.id, status=AdRequestStatusEnum.Accepted).count()
        rejected_request_count = AdRequest.query.filter_by(sponsor = current_user.id, status=AdRequestStatusEnum.Rejected).count()
        completed_request_count = AdRequest.query.filter_by(sponsor = current_user.id, status=AdRequestStatusEnum.Completed).count()
        stats['ad_request_stats'] = [accepted_request_count, rejected_request_count, completed_request_count]
        
        # return daily ad_requests groupby day sort ascending by date
        daily_ad_requests = db.session.query(func.count(AdRequest.id), func.date(AdRequest.created_at)).filter(AdRequest.sponsor == current_user.id).group_by(func.date(AdRequest.created_at)).order_by(func.date(AdRequest.created_at)).all()
        lables = []
        values = []
        cumulative = 0
        # fill missing dates from the first date to the last date
        if daily_ad_requests:
            first_date = daily_ad_requests[0][1]
            last_date = daily_ad_requests[-1][1]
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

        return render_template("sponsor/stats.html", stats=stats)
    else:
        return redirect(url_for("sponsor.login"))

    
@sponsor_bp.route("/find")
def find():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        return render_template("sponsor/find.html")
    else:
        return redirect(url_for("sponsor.find"))


@sponsor_bp.route("/ad_request/<int:ad_request_id>", methods=["GET", "POST"])
def ad_request(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        ad_request_id = request.view_args["ad_request_id"]
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        
        if ad_request is None:
            flash("Ad request not found.", "danger")
            return redirect(url_for("sponsor.campaigns"))
        
        elif ad_request.sponsor != current_user.id:
            flash("You are not authorized to view this ad request.", "danger")
            return redirect(url_for("sponsor.campaigns"))
        
        form = AdRequestUpdateForm(request.form)
        if form.validate_on_submit(): # update ad_request
            ad_request.name = form.name.data
            ad_request.budget = form.budget.data
            db.session.commit()
            flash("Ad request updated successfully.", "success")
            return redirect(url_for("sponsor.ad_request", ad_request_id=ad_request_id))
        
        influencer = Influencer.query.filter_by(id=ad_request.influencer).first()
        campaigns = Campaigns.query.filter_by(created_by=current_user.id).all()
        messages = Message.query.filter_by(ad_request=ad_request_id).all()
        form.name.data = ad_request.name
        form.budget.data = ad_request.budget
        form.campaign.data = ad_request.campaign
        return render_template("sponsor/ad_request.html", ad_request=ad_request, influencer=influencer, messages=messages, form=form, campaigns=campaigns, campaign_id=ad_request.campaign, AdRequestStatusEnum=AdRequestStatusEnum, AdRequestSenderEnum=AdRequestSenderEnum)
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/ad_request/<int:ad_request_id>/send_message", methods=["POST"])
def send_message(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        ad_request_id = request.view_args["ad_request_id"]
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        if ad_request.sponsor != current_user.id:
            flash("You are not authorized to send a message for this ad request.", "danger")
            return redirect(url_for("sponsor.campaigns"))
        
        form = AdRequestUpdateForm(request.form)
        message = Message(
            message=form.message.data,
            ad_request=ad_request_id,
            sender_name=current_user.name
        )
        db.session.add(message)
        db.session.commit()
        flash("Message sent successfully.", "success")
        return redirect(url_for("sponsor.ad_request", ad_request_id=ad_request_id))
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/ad_request/create/<int:influencer_id>", methods=["GET","POST"])
def create_ad_request(influencer_id):
    if current_user.is_authenticated and session.get("role") == "sponsor":
        influencer_id = request.view_args["influencer_id"]
        campaign_id = request.args.get("campaign_id")
        if campaign_id is not None :
            campaign_id = int(campaign_id)
        influencer = Influencer.query.filter_by(id=influencer_id).first()
        campaigns = Campaigns.query.filter_by(created_by=current_user.id).all()
        form = AdRequestForm(request.form)
        if (form.validate_on_submit()):
            ad_request = AdRequest(
                name = form.name.data,
                budget=form.budget.data,
                campaign=form.campaign.data,
                sponsor=current_user.id,
                influencer=influencer.id,
                sender=AdRequestSenderEnum.Sponsor
            )
            db.session.add(ad_request)
            db.session.commit()
            
            message = Message(
                message=form.message.data,
                ad_request=ad_request.id,
                sender_name=current_user.name
            )
            db.session.add(message)
            db.session.commit() 
            
            flash("Ad request Created successfully.", "success")
            return redirect(f"/sponsor/ad_request/{ad_request.id}")
        return render_template("sponsor/ad_request_form.html", influencer=influencer, form=form, campaigns=campaigns, campaign_id=campaign_id)
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/ad_request/response", methods=["POST"])
def respond_to_ad_request():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        form = AdRequestResponseForm(request.form)
        if form.validate_on_submit():
            ad_request = AdRequest.query.filter_by(id=form.ad_request_id.data).first()
            if ad_request.sponsor != current_user.id:
                flash("You are not authorized to respond to this ad request.", "danger")
                return redirect(url_for("sponsor.dashboard"))
            
            ad_request.status = form.response.data
            db.session.commit()
            flash(f"Ad request {ad_request.status.value} successfully.", "success")
            return redirect(url_for("sponsor.ad_request", ad_request_id=ad_request.id))
    else:
        return redirect(url_for("sponsor.login"))

@sponsor_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and session.get("role") == "sponsor":
        flash("You are already registered.", "info")
        return redirect(url_for("sponsor.dashboard"))
    form = SponsorRegisterForm(request.form)
    if form.validate_on_submit():
        # Handle file upload
        image_file = request.files.get("image")
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            filename = f"{int(time.time())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(upload_path)
        sponsor = Sponsor(
            email=form.email.data, 
            password=form.password.data,
            name=form.name.data,
            about=form.about.data,
            image=filename,
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



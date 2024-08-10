from flask import session, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from .forms import AdminLoginForm, AdminRegisterForm, SearchForm
from src.sponsor.forms import AdRequestUpdateForm
import os
from datetime import datetime, timedelta
from sqlalchemy import func

from src import bcrypt, db
from src.admin.models import Admin
from src.sponsor.models import Campaigns, VisibilityEnum, Sponsor
from src.influencer.models import Influencer
from src.core.models import AdRequest, AdRequestStatusEnum
from src.core.models import Message, AdRequestStatusEnum, AdRequestSenderEnum

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def dashboard():
    if current_user.is_authenticated and session.get("role") == "admin":
        campaigns = Campaigns.query.filter_by(flagged=False).all()
        flagged_campaigns = Campaigns.query.filter_by(flagged=True).all()
        flagged_sponsors = Sponsor.query.filter_by(flagged=True).all()
        flagged_influencers = Influencer.query.filter_by(flagged=True).all()
        return render_template("admin/dashboard.html", campaigns=campaigns, flagged_campaigns=flagged_campaigns, flagged_sponsors=flagged_sponsors, flagged_influencers=flagged_influencers)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/find", methods=["GET", "POST"])
def find():
    if current_user.is_authenticated and session.get("role") == "admin":
        
        form = SearchForm(request.form)
        if form.validate_on_submit():
            name = form.name.data
            campaigns = Campaigns.query.filter(Campaigns.name.ilike(f"%{name}%")).all()
            sponsors = Sponsor.query.filter(Sponsor.name.ilike(f"%{name}%")).all()
            influencers = Influencer.query.filter(Influencer.name.ilike(f"%{name}%")).all()
            return render_template("admin/find.html", campaigns=campaigns, sponsors=sponsors, influencers=influencers, form=form)
        
        campaigns = Campaigns.query.all()
        sponsors = Sponsor.query.all()
        influencers = Influencer.query.all()
        
        return render_template("admin/find.html", campaigns= campaigns, sponsors=sponsors, influencers=influencers, form=form)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/flag/campaigns/<int:campaign_id>", methods=["GET"])
def flag_campaign(campaign_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        campaign_id = request.view_args["campaign_id"]
        campaign = Campaigns.query.filter_by(id=campaign_id).first()
        campaign.flagged = True
        db.session.commit()
        flash("Campaign flagged.", "info")
        return redirect(url_for("admin.campaign_details", campaign_id=campaign_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/unflag/campaigns/<int:campaign_id>", methods=["GET"])
def unflag_campaign(campaign_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        campaign_id = request.view_args["campaign_id"]
        campaign = Campaigns.query.filter_by(id=campaign_id).first()
        campaign.flagged = False
        db.session.commit()
        flash("Campaign unflagged.", "info")
        return redirect(url_for("admin.campaign_details", campaign_id=campaign_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/campaigns/<int:campaign_id>", methods=["GET"])
def campaign_details(campaign_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        campaign_id = request.view_args["campaign_id"]
        campaign_data = Campaigns.query.filter_by(id=campaign_id).first()
        
        ad_requests = db.session.query(AdRequest, Sponsor, Influencer).\
            join(Sponsor, AdRequest.sponsor == Sponsor.id).\
            join(Influencer, AdRequest.influencer == Influencer.id).\
            filter(AdRequest.campaign == campaign_id).all()
        
        return render_template("admin/campaign_details.html", campaign=campaign_data, ad_requests=ad_requests, AdRequestStatusEnum=AdRequestStatusEnum)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/ad_request/<int:ad_request_id>", methods=['GET'])
def ad_request(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        
        if ad_request is None:
            flash("Ad request not found!", "danger")
            return redirect(url_for("influencer.requests"))
        
        influencer = Influencer.query.filter_by(id = current_user.id).first()
        campaign = Campaigns.query.filter_by(id = ad_request.campaign).first()
        messages = Message.query.filter_by(ad_request = ad_request_id )
        
        return render_template("admin/ad_request.html", ad_request=ad_request, influencer=influencer, messages=messages, campaign=campaign, AdRequestStatusEnum=AdRequestStatusEnum, AdRequestSenderEnum=AdRequestSenderEnum)
    else:
        return redirect(url_for("admin.login"))
   
@admin_bp.route("/flag/ad_request/<int:ad_request_id>", methods=["GET"])
def flag_ad_request(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        ad_request_id = request.view_args["ad_request_id"]
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        ad_request.flagged = True
        db.session.commit()
        flash("Ad request flagged.", "info")
        return redirect(url_for("admin.ad_request", ad_request_id=ad_request_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/unflag/ad_request/<int:ad_request_id>", methods=["GET"])
def unflag_ad_request(ad_request_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        ad_request_id = request.view_args["ad_request_id"]
        ad_request = AdRequest.query.filter_by(id=ad_request_id).first()
        ad_request.flagged = False
        db.session.commit()
        flash("Ad request unflagged.", "info")
        return redirect(url_for("admin.ad_request", ad_request_id=ad_request_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/sponsor/<int:sponsor_id>", methods=["GET"])
def sponsor_details(sponsor_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        sponsor_id = request.view_args["sponsor_id"]
        sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
        
        return render_template("admin/sponsor_profile.html", sponsor=sponsor)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/flag/sponsor/<int:sponsor_id>", methods=["GET"])
def flag_sponsor(sponsor_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        sponsor_id = request.view_args["sponsor_id"]
        sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
        sponsor.flagged = True
        db.session.commit()
        flash("Sponsor flagged.", "info")
        return redirect(url_for("admin.sponsor_details", sponsor_id=sponsor_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/unflag/sponsor/<int:sponsor_id>", methods=["GET"])
def unflag_sponsor(sponsor_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        sponsor_id = request.view_args["sponsor_id"]
        sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
        sponsor.flagged = False
        db.session.commit()
        flash("Sponsor unflagged.", "info")
        return redirect(url_for("admin.sponsor_details", sponsor_id=sponsor_id))
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/influencer/<int:influencer_id>", methods=["GET"])
def influencer_details(influencer_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        influencer_id = request.view_args["influencer_id"]
        influencer = Influencer.query.filter_by(id=influencer_id).first()
        
        return render_template("admin/influencer_profile.html", influencer=influencer)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/flag/influencer/<int:influencer_id>", methods=["GET"])
def flag_influencer(influencer_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        influencer_id = request.view_args["influencer_id"]
        influencer = Influencer.query.filter_by(id=influencer_id).first()
        influencer.flagged = True
        db.session.commit()
        flash("Influencer flagged.", "info")
        return redirect(url_for("admin.influencer_details", influencer_id=influencer_id))
    else:
        return redirect(url_for("admin.login"))
    
@admin_bp.route("/unflag/influencer/<int:influencer_id>", methods=["GET"])
def unflag_influencer(influencer_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        influencer_id = request.view_args["influencer_id"]
        influencer = Influencer.query.filter_by(id=influencer_id).first()
        influencer.flagged = False
        db.session.commit()
        flash("Influencer unflagged.", "info")
        return redirect(url_for("admin.influencer_details", influencer_id=influencer_id))
    else:
        return redirect(url_for("admin.login"))
    
# route to remove campaigns
@admin_bp.route("/remove/campaign/<int:campaign_id>", methods=["GET"])
def remove_campaign(campaign_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        campaign_id = request.view_args["campaign_id"]
        campaign = Campaigns.query.filter_by(id=campaign_id).first()
        ad_requests = AdRequest.query.filter_by(campaign=campaign_id).all()
        
        # remove all ad requests associated with the campaign
        for ad_request in ad_requests:
            # remove all messages associated with the ad request
            messages = Message.query.filter_by(ad_request=ad_request.id).all()
            for message in messages:
                db.session.delete(message)
                db.session.commit()
            db.session.delete(ad_request)
            db.session.commit()
        db.session.delete(campaign)
        db.session.commit()
        flash("Campaign removed.", "info")
        return redirect(url_for("admin.dashboard"))   
    else:
        return redirect(url_for("admin.login"))

# route to remove influencer
@admin_bp.route("/remove/influencer/<int:influencer_id>", methods=["GET"])
def remove_influencer(influencer_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        influencer_id = request.view_args["influencer_id"]
        influencer = Influencer.query.filter_by(id=influencer_id).first()
        ad_requests = AdRequest.query.filter_by(influencer=influencer_id).all()
        
        # remove all ad requests associated with the influencer
        for ad_request in ad_requests:
            # remove all messages associated with the ad request
            messages = Message.query.filter_by(ad_request=ad_request.id).all()
            for message in messages:
                db.session.delete(message)
                db.session.commit()
            db.session.delete(ad_request)
            db.session.commit()
        db.session.delete(influencer)
        db.session.commit()
        flash("Influencer removed.", "info")
        return redirect(url_for("admin.dashboard"))   
    else:
        return redirect(url_for("admin.login"))

# route to remove sponsor
@admin_bp.route("/remove/sponsor/<int:sponsor_id>", methods=["GET"])
def remove_sponsor(sponsor_id):
    if current_user.is_authenticated and session.get("role") == "admin":
        sponsor_id = request.view_args["sponsor_id"]
        sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
        ad_requests = AdRequest.query.filter_by(sponsor=sponsor_id).all()
        campaigns = Campaigns.query.filter_by(sponsor=sponsor_id).all()
        
        # remove all ad requests associated with the sponsor
        for ad_request in ad_requests:
            # remove all messages associated with the ad request
            messages = Message.query.filter_by(ad_request=ad_request.id).all()
            for message in messages:
                db.session.delete(message)
                db.session.commit()
            db.session.delete(ad_request)
            db.session.commit()
        
        # remove all campaigns associated with the sponsor
        for campaign in campaigns:
            ad_requests = AdRequest.query.filter_by(campaign=campaign.id).all()
            for ad_request in ad_requests:
                # remove all messages associated with the ad request
                messages = Message.query.filter_by(ad_request=ad_request.id).all()
                for message in messages:
                    db.session.delete(message)
                    db.session.commit()
                db.session.delete(ad_request)
                db.session.commit()
            db.session.delete(campaign)
            db.session.commit()
        
        
        db.session.delete(sponsor)
        db.session.commit()
        flash("Sponsor removed.", "info")
        return redirect(url_for("admin.dashboard"))   
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/stats")
def stats():
    if current_user.is_authenticated and session.get("role") == "admin":
        
        stats = {}
        ad_requests_count = AdRequest.query.count()
        stats['ad_requests_count'] = ad_requests_count
        
        accepted_request_count = AdRequest.query.filter_by(status=AdRequestStatusEnum.Accepted).count()
        rejected_request_count = AdRequest.query.filter_by(status=AdRequestStatusEnum.Rejected).count()
        completed_request_count = AdRequest.query.filter_by(status=AdRequestStatusEnum.Completed).count()
        stats['ad_request_stats'] = [accepted_request_count, rejected_request_count, completed_request_count]
        
        # return daily ad_requests groupby day sort ascending by date
        daily_ad_requests = db.session.query(func.count(AdRequest.id), func.date(AdRequest.created_at)).group_by(func.date(AdRequest.created_at)).order_by(func.date(AdRequest.created_at)).all()
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
        
        daily_messages = db.session.query(func.count(Message.id), func.date(Message.sent_time)).group_by(func.date(Message.sent_time)).order_by(func.date(Message.sent_time)).all()
        lables = []
        values = []
        cumulative = 0
        # fill missing dates from the first date to the last date
        if daily_messages:
            first_date = daily_messages[0][1]
            last_date = daily_messages[-1][1]
            date = first_date
            while date <= last_date:
                lables.append(date.strftime('%Y-%m-%d'))
                for message in daily_messages:
                    if message[1] == date:
                        cumulative += message[0]
                        values.append(cumulative)
                        break
                else:
                    values.append(cumulative)
                date += timedelta(days=1)
        
        stats['daily_messages'] = {'labels': lables, 'values': values}
        
        daily_sponsors = db.session.query(func.count(Sponsor.id), func.date(Sponsor.created_on)).group_by(func.date(Sponsor.created_on)).order_by(func.date(Sponsor.created_on)).all()
        lables = []
        values = []
        cumulative = 0
        # fill missing dates from the first date to the last date
        
        if daily_sponsors:
            first_date = daily_sponsors[0][1]
            last_date = daily_sponsors[-1][1]
            date = first_date
            while date <= last_date:
                lables.append(date.strftime('%Y-%m-%d'))
                for sponsor in daily_sponsors:
                    if sponsor[1] == date:
                        cumulative += sponsor[0]
                        values.append(cumulative)
                        break
                else:
                    values.append(cumulative)
                date += timedelta(days=1)
        
        stats['daily_sponsors'] = {'labels': lables, 'values': values}
        
        daily_influencers = db.session.query(func.count(Influencer.id), func.date(Influencer.created_on)).group_by(func.date(Influencer.created_on)).order_by(func.date(Influencer.created_on)).all()
        lables = []
        values = []
        cumulative = 0
        
        if daily_influencers:
            first_date = daily_influencers[0][1]
            last_date = daily_influencers[-1][1]
            date = first_date
            while date <= last_date:
                lables.append(date.strftime('%Y-%m-%d'))
                for influencer in daily_influencers:
                    if influencer[1] == date:
                        cumulative += influencer[0]
                        values.append(cumulative)
                        break
                else:
                    values.append(cumulative)
                date += timedelta(days=1)
                
        stats['daily_influencers'] = {'labels': lables, 'values': values}   
        
        print(stats)
        return render_template("admin/stats.html", stats=stats)
    else:
        return redirect(url_for("admin.login"))

@admin_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and session.get("role") == "admin":
        flash("You are already registered.", "info")
        return redirect(url_for("admin.dashboard"))
    form = AdminRegisterForm(request.form)
    if form.validate_on_submit():
        admin = Admin(email=form.email.data, password=form.password.data)
        db.session.add(admin)
        db.session.commit() 
        
        session["role"] = "admin"  # add role to session
        login_user(admin)
        flash("You registered and are now logged in. Welcome!", "success")
        
        return redirect(url_for("admin.dashboard"))
    
    return render_template("admin/register.html", form=form)

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and session.get("role") == "admin":
        flash("You are already registered.", "info")
        return redirect(url_for("admin.dashboard"))
    
    form = AdminLoginForm(request.form)
    
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        print(user.password)
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            session["role"] = "admin"  # add role to session
            login_user(user)           
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("admin/login.html", form=form)

    
    # This is for handling a GET request
    return render_template("admin/login.html", form=form)

@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("admin.login"))



from flask import session, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from .forms import AdminLoginForm, AdminRegisterForm
import os

from src import bcrypt, db
from src.admin.models import Admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated and session.get("role") == "admin":
        return render_template("admin/dashboard.html")
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



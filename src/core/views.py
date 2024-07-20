from flask import Blueprint, render_template, session
from flask_login import login_required

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def home():
    role = session.get("role")
    return render_template("core/index.html", role=role)

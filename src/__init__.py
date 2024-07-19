from decouple import config
from flask import Flask, render_template, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Registering blueprints
from src.core.views import core_bp
from src.admin.views import admin_bp
from src.sponsor.views import sponsor_bp

app.register_blueprint(core_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(sponsor_bp, url_prefix="/sponsor")

from src.admin.models import Admin
from src.sponsor.models import Sponsor

login_manager.login_view = "sponsor.login"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    if session.get("role") == "admin":
        return Admin.query.filter(Admin.id == int(user_id)).first()
    elif session.get("role") == "sponsor":
        return Sponsor.query.filter(Sponsor.id == int(user_id)).first()
    return None

@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

# ====================================
# GLOBAL EXTENSIONS
# ====================================
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()  # untuk Google Login

# ====================================
# APP FACTORY
# ====================================
def create_app():
    load_dotenv()  # load .env

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))        # /app
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))     # root project
    TEMPLATE_DIR = os.path.join(ROOT_DIR, "templates")
    STATIC_DIR   = os.path.join(ROOT_DIR, "static")

    # ====================================
    # FLASK APP
    # ====================================
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR
    )

    # ====================================
    # DATABASE CONFIG
    # ====================================
    if os.getenv("FLY_APP_NAME"):     # Running on Fly.io
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/data.db'
    else:                              # Running locally
        local_db = os.path.join(ROOT_DIR, "instance", "data.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{local_db}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")

    # ====================================
    # INIT EXTENSIONS
    # ====================================
    db.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)

    # ====================================
    # GOOGLE AUTH CONFIG
    # ====================================
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v2/',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
        client_kwargs={'scope': 'openid email profile'}
    )

    # ====================================
    # BLUEPRINTS
    # ====================================
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.report.routes import report_bp
    from app.project.routes import project_bp
    from app.profiles.routes import profiles_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,      url_prefix="/auth")
    app.register_blueprint(report_bp,    url_prefix="/report")
    app.register_blueprint(project_bp,   url_prefix="/project")
    app.register_blueprint(profiles_bp,  url_prefix="/profile")
    app.register_blueprint(admin_bp,     url_prefix="/admin")

    return app

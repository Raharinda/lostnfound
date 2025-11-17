import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMPLATE_DIR = os.path.join(BASE_DIR, '../templates')
    STATIC_DIR = os.path.join(BASE_DIR, '../static')

    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # root project folder (naik 1 folder dari /app)
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

    if os.getenv("FLY_APP_NAME"):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/data.db'
    else:
        local_db = os.path.join(ROOT_DIR, "instance", "data.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{local_db}"


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey'

    db.init_app(app)
    migrate.init_app(app, db)

    # REGISTER BLUEPRINTS
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.report.routes import report_bp

    from .report import edit_routes
    from .report import delete_routes

    from app.project.routes import project_bp
    from app.profiles.routes import profiles_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(project_bp, url_prefix='/project')
    app.register_blueprint(profiles_bp, url_prefix='/profile')

    return app

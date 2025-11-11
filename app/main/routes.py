from flask import Blueprint, render_template
from app.models import Report

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('index.html', reports=reports)

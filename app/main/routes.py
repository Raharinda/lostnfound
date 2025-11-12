from flask import Blueprint, render_template, request
from app.models import Report
from sqlalchemy import or_

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    # Ambil parameter pencarian dari query string (misal: ?q=dompet)
    query = request.args.get('q', '').strip()

    if query:
        # Kalau ada keyword, cari berdasarkan item_name ATAU location
        reports = Report.query.filter(
            or_(
                Report.item_name.ilike(f"%{query}%"),
                Report.location.ilike(f"%{query}%"),
                Report.description.ilike(f"%{query}%")
            )
        ).order_by(Report.id.desc()).all()
    else:
        # Kalau gak ada keyword, tampilkan semua laporan
        reports = Report.query.order_by(Report.id.desc()).all()

    return render_template('index.html', reports=reports, query=query)

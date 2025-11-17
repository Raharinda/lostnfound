from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import db, Report
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')

def is_admin():
    # sementara: user id 1 = admin
    return session.get("user_id") == 1

# --- ADMIN PANEL: LIST ALL REPORTS ---
@admin_bp.route('/reports')
def admin_reports():
    if not is_admin():
        flash("Akses ditolak! Kamu bukan admin.", "danger")
        return redirect(url_for('main_bp.index'))

    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('admin/reports.html', reports=reports)

# --- DELETE REPORT ---
@admin_bp.route('/reports/delete/<int:report_id>')
def admin_delete_report(report_id):
    if not is_admin():
        flash("Akses ditolak!", "danger")
        return redirect(url_for('main_bp.index'))

    report = Report.query.get(report_id)

    if not report:
        flash("Report tidak ditemukan.", "warning")
        return redirect(url_for('admin_bp.admin_reports'))

    # Hard delete langsung
    db.session.delete(report)
    db.session.commit()

    flash("Report berhasil dihapus.", "success")
    return redirect(url_for('admin_bp.admin_reports'))

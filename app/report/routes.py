from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Report, db
from datetime import timezone
import pytz

report_bp = Blueprint('report_bp', __name__, template_folder='templates')

# 🧾 ROUTE: Buat dan tampilkan laporan
@report_bp.route('/', methods=['GET', 'POST'], endpoint='report')
def report_page():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Login dulu sebelum melapor!', 'warning')
            return redirect(url_for('auth_bp.login'))

        new_report = Report(
            user_id=session['user_id'],
            name=session['username'],
            item_name=request.form['item_name'],
            description=request.form['description'],
            location=request.form['location'],
            contact=request.form['contact'],
            report_type=request.form.get('report_type', 'lost')
        )

        db.session.add(new_report)
        db.session.commit()

        flash('Laporan berhasil dikirim!', 'success')
        return redirect(url_for('main_bp.index'))

    reports = Report.query.all()

    # 🔁 Konversi waktu UTC ke WIB sebelum dikirim ke template
    jakarta = pytz.timezone('Asia/Jakarta')
    for r in reports:
        if r.created_at:
            if r.created_at.tzinfo is None:
                r.created_at = pytz.utc.localize(r.created_at)
            r.created_at = r.created_at.astimezone(jakarta)

    return render_template('report/index.html', reports=reports)

# 🧾 ROUTE: Edit laporan
@report_bp.route('/edit/<int:report_id>', methods=['GET', 'POST'], endpoint='edit_report')
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)

    # pastikan user login & pemilik laporan
    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk mengedit laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))

    if request.method == 'POST':
        report.item_name = request.form['item_name']
        report.description = request.form['description']
        report.location = request.form['location']
        report.contact = request.form['contact']
        report.status = request.form['status']
        db.session.commit()
        flash('Laporan berhasil diperbarui!', 'success')
        return redirect(url_for('profiles_bp.profile'))

    return render_template('report/edit_report.html', report=report)

# 🗑️ ROUTE: Hapus laporan
@report_bp.route('/delete/<int:report_id>', methods=['GET'], endpoint='delete_report')
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    # pastikan user yang login adalah pemilik laporan
    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk menghapus laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))

    db.session.delete(report)
    db.session.commit()
    flash('Laporan berhasil dihapus.', 'info')
    return redirect(url_for('profiles_bp.profile'))

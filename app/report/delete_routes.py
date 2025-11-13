from flask import redirect, url_for, flash, session
from app.models import Report, db
from app.report.routes import report_bp

@report_bp.route('/delete/<int:report_id>', methods=['GET'], endpoint='delete_report')
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk menghapus laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))

    db.session.delete(report)
    db.session.commit()

    flash('Laporan berhasil dihapus.', 'info')
    return redirect(url_for('profiles_bp.profile'))

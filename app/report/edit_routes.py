from flask import render_template, request, redirect, url_for, flash, session
from app.models import Report, db
from app.report.routes import report_bp

@report_bp.route('/edit/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk mengedit laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))
    
    if request.method == 'POST':
        report.item_name = request.form['item_name']
        report.description = request.form.get('description')
        report.location = request.form['location']
        report.contact = request.form['contact']
        report.status = request.form['status']
        db.session.commit()
        flash('Laporan berhasil diperbarui!', 'success')
        return redirect(url_for('profiles_bp.profile'))
    
    return render_template('report/edit_report.html', report=report)

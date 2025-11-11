from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Report

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/', methods=['GET', 'POST'])
def report():
    if 'user_id' not in session:
        flash('Login dulu sebelum membuat laporan!', 'danger')
        return redirect(url_for('auth_bp.login'))

    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']

        new_report = Report(
            user_id=session['user_id'],
            name=session['username'],
            item_name=item_name,
            description=description,
            location=location,
            contact=contact
        )
        db.session.add(new_report)
        db.session.commit()

        flash('Laporan berhasil dikirim!', 'success')
        return redirect(url_for('main_bp.index'))  # kembali ke homepage

    return render_template('report/index.html')

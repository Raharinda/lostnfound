from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models import Report, db
import os, uuid

report_bp = Blueprint('report_bp', __name__, template_folder='templates')

@report_bp.route('/', methods=['GET', 'POST'], endpoint='report')
def report_page():

    if 'user_id' not in session:
        flash('Login dulu sebelum melapor!', 'warning')
        return redirect(url_for('auth_bp.login'))

    if request.method == 'POST':
        file = request.files.get('image')
        filename = None

        if file and file.filename.strip():
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"

            upload_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'static', 'uploads'))
            os.makedirs(upload_dir, exist_ok=True)

            file.save(os.path.join(upload_dir, filename))

        new_report = Report(
            user_id=session['user_id'],
            name=session['username'],
            item_name=request.form['item_name'],
            description=request.form.get('description'),
            location=request.form['location'],
            contact=request.form['contact'],
            report_type=request.form.get('report_type', 'lost'),
            image_url=filename
        )

        db.session.add(new_report)
        db.session.commit()

        flash('Laporan berhasil dikirim!', 'success')
        return redirect(url_for('main_bp.index'))

    reports = Report.query.all()
    return render_template('report/index.html', reports=reports)

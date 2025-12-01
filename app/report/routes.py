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


@report_bp.route('/edit/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Verifikasi user punya akses ke laporan ini
    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk mengedit laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))
    
    if request.method == 'POST':
        # Update gambar jika ada file baru
        file = request.files.get('image')
        if file and file.filename.strip():
            # Hapus gambar lama jika ada
            if report.image_url:
                old_file = os.path.join(current_app.root_path, '..', 'static', 'uploads', report.image_url)
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Simpan gambar baru
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            upload_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'static', 'uploads'))
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            report.image_url = filename
        
        # Update data laporan
        report.item_name = request.form['item_name']
        report.description = request.form.get('description')
        report.location = request.form['location']
        report.contact = request.form['contact']
        report.status = request.form.get('status', report.status)
        
        db.session.commit()
        flash('Laporan berhasil diperbarui!', 'success')
        return redirect(url_for('profiles_bp.profile'))
    
    return render_template('report/edit_report.html', report=report)

@report_bp.route('/delete/<int:report_id>', methods=['GET', 'POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Verifikasi user punya akses
    if 'user_id' not in session or report.user_id != session['user_id']:
        flash('Kamu tidak punya izin untuk menghapus laporan ini.', 'danger')
        return redirect(url_for('profiles_bp.profile'))
    
    # Hapus gambar jika ada
    if report.image_url:
        image_path = os.path.join(current_app.root_path, '..', 'static', 'uploads', report.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Hapus record dari database
    db.session.delete(report)
    db.session.commit()
    
    flash('Laporan berhasil dihapus!', 'success')
    return redirect(url_for('profiles_bp.profile'))
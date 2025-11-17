from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import User, Report

profiles_bp = Blueprint('profiles_bp', __name__, template_folder='templates')

@profiles_bp.route('/', methods=['GET'])
def profile():
    # User belum login (session kosong)
    if 'user_id' not in session:
        flash('Kamu harus login dulu untuk membuka profil!', 'warning')
        return redirect(url_for('auth_bp.login'))

    # Ambil user dari database
    user = User.query.get(session['user_id'])

    # Kalau user_id ada di session tapi user-nya sudah hilang
    if user is None:
        flash('Akun tidak ditemukan. Silakan login ulang.', 'danger')
        session.clear()
        return redirect(url_for('auth_bp.login'))

    # Ambil laporan
    reports = Report.query.filter_by(user_id=user.id).all()

    return render_template('profiles/profile.html', user=user, reports=reports)


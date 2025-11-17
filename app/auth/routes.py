from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import oauth
from app.models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!', 'danger')
            return redirect(url_for('auth_bp.signup'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrasi berhasil! Silakan login.', 'success')
        return render_template('auth/signup_success.html', username=username)
    return render_template('auth/signup.html')

@auth_bp.route("/login/google")
def google_login():
    redirect_uri = url_for("auth_bp.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.userinfo()

    email = user_info.get("email")
    name = user_info.get("name")

    # cek apakah user sudah ada
    user = User.query.filter_by(email=email).first()

    if not user:
    # auto-register untuk user dari Google
        user = User(username=name, email=email)
        user.set_password(os.urandom(16).hex())  # password dummy biar tidak null
        db.session.add(user)
        db.session.commit()


    # login user
    session["user_id"] = user.id
    session["username"] = user.username

    flash(f"Selamat datang, {user.username}!", "success")
    return redirect(url_for("main_bp.index"))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('main_bp.index'))
        flash('Email atau password salah!', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Kamu telah logout.', 'info')
    return redirect(url_for('auth_bp.login'))

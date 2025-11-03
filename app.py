# app.py
"""
Lost & Found - Flask application
Designed for use in a campus environment (UGM) as a group project base.
Features:
 - SQLite DB (reports + users)
 - File upload for images (with allowed extensions, unique filenames)
 - Index with search + pagination
 - Report creation (form POST)
 - Detail view
 - Simple admin interface (login/logout) to manage reports
 - JSON API endpoints for integration
 - CLI helper to init DB or create admin user
"""

import os
import sqlite3
from uuid import uuid4
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_from_directory, session, jsonify, abort
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------
# CONFIGURATION
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'database', 'lostfound.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['DATABASE'] = os.environ.get('LF_DATABASE', DEFAULT_DB_PATH)
app.config['UPLOAD_FOLDER'] = os.environ.get('LF_UPLOAD_FOLDER', UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('LF_MAX_CONTENT', MAX_CONTENT_LENGTH))
app.secret_key = os.environ.get('LF_SECRET_KEY', 'change-this-secret-in-production')

# Ensure folders exist
os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ---------------------------
# DATABASE HELPERS
# ---------------------------
def get_db():
    """Return a sqlite3 connection with row factory (dict-like access)."""
    conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create necessary tables if not exist."""
    conn = get_db()
    cur = conn.cursor()
    # Reports table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter TEXT NOT NULL,
        item_name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        image_path TEXT,
        location TEXT,
        status TEXT DEFAULT 'lost',  -- 'lost' or 'found' or 'claimed'
        created_at TEXT NOT NULL
    )
    """)
    # Users table for admin accounts (username unique)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()


# ---------------------------
# AUTH HELPERS (simple session-based)
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def create_user(username: str, password: str, full_name: str = None, is_admin: bool = True):
    """Create a user with hashed password. Returns True if created, False on duplicate."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), full_name, int(is_admin))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None


# ---------------------------
# UTILITIES
# ---------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage):
    """Save an uploaded file with a randomized filename to avoid collisions.
       Returns relative path to saved file (from static folder) or None.
    """
    if not file_storage:
        return None
    filename = file_storage.filename
    if filename == '' or not allowed_file(filename):
        return None

    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}.{ext}"
    secure_name = secure_filename(unique_name)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
    file_storage.save(save_path)
    # Return path relative to app root, so templates can use url_for('static', filename=...)
    rel_path = os.path.relpath(save_path, BASE_DIR)
    return rel_path.replace("\\", "/")


# ---------------------------
# ROUTES: FRONTEND
# ---------------------------
@app.route('/')
def index():
    """
    Homepage:
     - supports ?q=search query
     - supports ?status=lost/found/claimed
     - supports pagination ?page=1 (10 per page)
    """
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip().lower()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    per_page = 9
    offset = (page - 1) * per_page

    db = get_db()
    base_sql = "SELECT * FROM reports"
    params = []
    where_clauses = []
    if q:
        where_clauses.append("(item_name LIKE ? OR description LIKE ? OR reporter LIKE ? OR location LIKE ?)")
        qlike = f"%{q}%"
        params.extend([qlike, qlike, qlike, qlike])
    if status in {'lost', 'found', 'claimed'}:
        where_clauses.append("status = ?")
        params.append(status)

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    total_count = db.execute(f"SELECT COUNT(*) as c FROM ({base_sql})", params).fetchone()['c']
    rows = db.execute(base_sql + " ORDER BY created_at DESC LIMIT ? OFFSET ?", params + [per_page, offset]).fetchall()
    db.close()

    # simple pagination meta
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('index.html', reports=rows, q=q, status=status, page=page, total_pages=total_pages)


@app.route('/report', methods=['GET', 'POST'])
def report():
    """Form to create a new report (lost or found)."""
    if request.method == 'POST':
        reporter = request.form.get('reporter', '').strip()
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip() or None
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip() or None
        status = request.form.get('status', 'lost').strip().lower()
        if status not in {'lost', 'found'}:
            status = 'lost'

        if not reporter or not item_name or not description:
            flash("Harap isi semua field yang diperlukan: Nama Pelapor, Nama Barang, dan Deskripsi.", "danger")
            return redirect(url_for('report'))

        # handle file
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            image_path = save_uploaded_file(file)

        conn = get_db()
        conn.execute(
            """
            INSERT INTO reports (reporter, item_name, category, description, image_path, location, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (reporter, item_name, category, description, image_path, location, status, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        flash("Laporan berhasil disimpan. Terima kasih!", "success")
        return redirect(url_for('index'))

    # GET
    return render_template('report.html')


@app.route('/detail/<int:report_id>')
def detail(report_id):
    conn = get_db()
    report = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    if not report:
        abort(404, "Laporan tidak ditemukan")
    return render_template('detail.html', report=report)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files. Note: static folder already serves them, but provide route for convenience."""
    # filename is path relative to BASE_DIR (we stored relative path), but we want filename part in upload dir
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------------------------
# ROUTES: ADMIN (simple)
# ---------------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = authenticate_user(username, password)
        if user and user.get('is_admin'):
            # create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Selamat datang, {user.get('full_name') or user['username']}", "success")
            next_url = request.args.get('next') or url_for('admin_dashboard')
            return redirect(next_url)
        else:
            flash("Login gagal. Pastikan username/password benar dan akun memiliki hak admin.", "danger")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash("Anda berhasil logout.", "info")
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_dashboard():
    # list reports with simple management actions
    conn = get_db()
    reports = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', reports=reports)


@app.route('/admin/delete/<int:report_id>', methods=['POST'])
@login_required
def admin_delete(report_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        conn.close()
        flash("Laporan tidak ditemukan.", "warning")
        return redirect(url_for('admin_dashboard'))

    # delete image file if exists
    image_path = row['image_path']
    if image_path:
        # image_path stored as relative path from project root; convert to absolute
        abs_img_path = os.path.join(BASE_DIR, image_path)
        try:
            if os.path.exists(abs_img_path):
                os.remove(abs_img_path)
        except Exception as e:
            app.logger.warning("Gagal menghapus file gambar: %s", e)

    conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
    flash("Laporan berhasil dihapus.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/mark/<int:report_id>', methods=['POST'])
@login_required
def admin_mark(report_id):
    """Toggle status to claimed or update status via form param 'new_status'."""
    new_status = request.form.get('new_status', '').strip().lower()
    if new_status not in {'lost', 'found', 'claimed'}:
        flash("Status tidak valid.", "warning")
        return redirect(url_for('admin_dashboard'))
    conn = get_db()
    conn.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()
    flash("Status laporan diperbarui.", "success")
    return redirect(url_for('admin_dashboard'))


# ---------------------------
# ROUTES: API (lightweight)
# ---------------------------
@app.route('/api/reports', methods=['GET'])
def api_list_reports():
    """Return JSON list of reports with optional ?status=&q=&limit=&offset="""
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip().lower()
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    sql = "SELECT id, reporter, item_name, category, description, image_path, location, status, created_at FROM reports"
    params = []
    where = []
    if q:
        where.append("(item_name LIKE ? OR description LIKE ? OR reporter LIKE ? OR location LIKE ?)")
        qlike = f"%{q}%"
        params.extend([qlike, qlike, qlike, qlike])
    if status in {'lost', 'found', 'claimed'}:
        where.append("status = ?")
        params.append(status)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    return jsonify({"count": len(results), "results": results})


@app.route('/api/reports', methods=['POST'])
def api_create_report():
    """Create report via JSON. Expects application/json with keys:
        reporter, item_name, description, category (optional), location (optional), status (lost|found)
       NOTE: for image upload use multipart/form-data on /report form, not JSON.
    """
    if not request.is_json:
        return jsonify({"error": "Content-type must be application/json"}), 400
    data = request.get_json()
    reporter = (data.get('reporter') or '').strip()
    item_name = (data.get('item_name') or '').strip()
    description = (data.get('description') or '').strip()
    category = data.get('category')
    location = data.get('location')
    status = (data.get('status') or 'lost').lower()
    if not reporter or not item_name or not description:
        return jsonify({"error": "Missing required fields"}), 400
    if status not in {'lost', 'found'}:
        status = 'lost'

    conn = get_db()
    conn.execute(
        "INSERT INTO reports (reporter, item_name, category, description, image_path, location, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (reporter, item_name, category, description, None, location, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True}), 201


# ---------------------------
# CLI Helpers (run via command line)
# ---------------------------
def print_help():
    print("Usage:")
    print("  python app.py run           # run dev server")
    print("  python app.py init_db       # create database and tables")
    print("  python app.py create_admin <username> <password> [full_name]  # create admin user")


# ---------------------------
# STARTUP
# ---------------------------
if __name__ == '__main__':
    import sys

    # Ensure DB exists
    init_db()

    # CLI options
    if len(sys.argv) >= 2:
        cmd = sys.argv[1].lower()
        if cmd == 'init_db':
            init_db()
            print("Database initialized at:", app.config['DATABASE'])
            sys.exit(0)
        elif cmd == 'create_admin':
            if len(sys.argv) < 4:
                print("Missing arguments. Example:\n  python app.py create_admin admin StrongPass123 'Admin Name'")
                sys.exit(1)
            username = sys.argv[2]
            password = sys.argv[3]
            full_name = sys.argv[4] if len(sys.argv) >= 5 else None
            ok = create_user(username, password, full_name, is_admin=True)
            if ok:
                print(f"Admin user '{username}' created.")
            else:
                print(f"Failed to create admin '{username}': username already exists.")
            sys.exit(0)
        elif cmd == 'help':
            print_help()
            sys.exit(0)
        elif cmd == 'run':
            # run below to actually start the dev server
            pass
        else:
            print("Unknown command.")
            print_help()
            sys.exit(1)

    # default: start flask dev server
    app.run(host='0.0.0.0', port=5000, debug=True)

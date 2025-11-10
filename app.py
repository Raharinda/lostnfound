from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

# ====== ROUTE UTAMA ======
@app.route('/')
def index():
    return render_template('index.html')  # dashboard utama

# ====== ROUTE TAMBAHAN UNTUK NAVBAR ======
@app.route('/navbar')
def navbar():
    return render_template('navbar.html')  # ini render file navbar.html

# ====== FITUR TAMBAHAN ======
@app.route('/search')
def search():
    query = request.args.get('q', '')
    print(f"Pencarian: {query}")
    # Tambahkan logika pencarian di sini
    return redirect('/')

@app.route('/notifications')
def notifications():
    return "Halaman Notifikasi"

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return "Halaman Profile"

@app.route('/new-project')
def new_project():
    return "Halaman New Project"

@app.route('/get-code')
def get_code():
    return "Halaman Get Code"

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    # misal nanti kamu tambahkan logic dark/light mode
    return jsonify({'success': True})


# ====== RUNNING SERVER ======
if __name__ == '__main__':
    app.run(debug=True)

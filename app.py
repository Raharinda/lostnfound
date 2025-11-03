from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    print(f"Pencarian: {query}")
    # Proses pencarian di sini
    return redirect('/')

@app.route('/notifications')
def notifications():
    return "Halaman Notifikasi"

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
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
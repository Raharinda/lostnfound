from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ====== KONFIG DATABASE ======
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ====== MODEL DATABASE ======
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Project {self.title}>'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Belum ditemukan")

    def __repr__(self):
        return f'<Report {self.item_name}>'

# ====== ROUTE ======
@app.route('/')
def index():
    reports = Report.query.all()
    return render_template('index.html', reports=reports)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        name = request.form['name']
        item_name = request.form['item_name']
        description = request.form['description']
        location = request.form['location']
        contact = request.form['contact']

        new_report = Report(
            name=name,
            item_name=item_name,
            description=description,
            location=location,
            contact=contact
        )

        db.session.add(new_report)
        db.session.commit()
        return redirect('/')

    return render_template('report/index.html')

@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    projects = Project.query.filter(Project.title.contains(query)).all()
    return render_template('index.html', projects=projects)

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
    users = User.query.all()
    return render_template('profile.html', users=users)

@app.route('/new-project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_project = Project(title=title, description=description)
        db.session.add(new_project)
        db.session.commit()
        return redirect('/')
    return render_template('new_project.html')

@app.route('/get-code')
def get_code():
    return "Halaman Get Code"

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    return jsonify({'success': True})


# ====== RUN APP ======
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Flask, render_template, url_for

# kontol

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/report')
def report():
    return render_template('/report/reportFound.html')

if __name__ == '__main__':
    app.run(debug=True)

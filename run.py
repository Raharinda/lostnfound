from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # ← penting! ini yang bikin file data.db dan tabelnya
    app.run(debug=True)

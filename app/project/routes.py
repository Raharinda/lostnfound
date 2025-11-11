from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Project

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('/', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_project = Project(title=title, description=description)
        db.session.add(new_project)
        db.session.commit()
        flash('Project berhasil ditambahkan!', 'success')
        return redirect(url_for('main_bp.index'))

    projects = Project.query.all()
    return render_template('project/index.html', projects=projects)

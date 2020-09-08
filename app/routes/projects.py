from app.models import Project, Client, Asset, Topic, db
from app.forms import ProjectForm, CategoryForm
from flask import render_template, Response, Blueprint, redirect
from flask_login import login_required
from flask_api import status

# Define the blueprint: 'project', set its url prefix: app.url/
bp = Blueprint('project', __name__, url_prefix='/projects')


@bp.route('/')
@login_required
def projects():
    """
    Projects page.
    """
    projects = Project.query.all()
    if len(projects) == 0:
        return redirect("/")
    return render_template('projects/projects.html', projects=projects)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_project():
    """
    Allows users to create a new project.
    """
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data)
        db.session.add(project)

        topic = Topic(name=form.name.data, project=project)
        db.session.add(topic)

        db.session.commit()
        return redirect('/projects/{}'.format(project.name))
          
    if (form.errors):
        return render_template('projects/new_project.html', form=form), status.HTTP_303_SEE_OTHER

    return render_template('projects/new_project.html', form=form)


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    """
    Allows user to delete an existing project.
    """
    project = Project.query.get_or_404(id)

    for client in project.clients:
        db.session.delete(client)

    for asset in project.assets:
        db.session.delete(asset)

    for category in project.categories:
        db.session.delete(category)

    for subscription in project.subscriptions:
        db.session.delete(subscription)

    for topic in project.topics:
       db.session.delete(topic)

    db.session.delete(project)
    db.session.commit()
    return Response(status=status.HTTP_200_OK)


@bp.route('/<string:name>', defaults={'optional': None}, methods=['GET'])
@bp.route('/<string:name>/<string:optional>', methods=['GET'])
@login_required
def project(name, optional):
    """
    Retrieve information about a project.
    """
    project = Project.query.filter_by(name=name).first()
    if not project:
        return render_template('404.html'), 404

    if optional == "clients":
        return render_template('clients/clients.html', project=project)

    if optional == "categories":
        return render_template('categories/categories.html', project=project)

    if optional == "assets":
        return render_template('assets/assets.html', project=project)

    if optional == "subscriptions":
        return render_template('subscriptions/subscriptions.html', project=project)

    if optional == "topics":
        return render_template('topics/topics.html', project=project)

    return render_template('projects/project.html', project=project)

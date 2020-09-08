from flask import Blueprint, render_template, redirect, Response, make_response, jsonify
from flask_login import login_required
from flask_api import status
from app.models import Project, Topic, db
from app.forms import TopicForm
from app.schemas import topics_schema
import json

# Define the blueprint: 'topic', set its url prefix: app.url /topics
bp = Blueprint('topic', __name__, url_prefix='/topics')


@bp.route('/json/<int:project_id>', methods=['GET'])
@login_required
def topics_json(project_id):
    project = Project.query.get_or_404(project_id)
    topics = topics_schema.dump(project.topics)
    for topic in topics:
        m_topic = Topic.query.get_or_404(topic['id'])
        topic['text'] = str(m_topic)
    return make_response(jsonify({"topics": topics}))


@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_topic(project_id):
    """
    Allows user to creates a new topic.
    """
    project = Project.query.get_or_404(project_id)
    form = TopicForm()
    if form.validate_on_submit():
        topic = Topic(name=form.name.data, project=project)

        if form.parent.data:
            parent = Topic.query.get_or_404(form.parent.data)
            topic.parent = parent

        db.session.add(topic)
        db.session.commit()
        return redirect('/projects/{}/topics'.format(project.name))
        
    if form.errors:
        return render_template('topics/new_topic.html', project=project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('topics/new_topic.html', project=project, form=form)


@bp.route('/subtopics/<int:id>', methods=['GET'])
@login_required
def get_subtopics(id):
    topic = Topic.query.get_or_404(id)
    subtopics = Topic.query.filter_by(parent=topic)
    subtopics = topics_schema.dump(subtopics)
    return make_response(jsonify({"subtopics": subtopics}))


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_topics(id):
    """
    Allows user to delete an existing subscription.
    """
    topic = Topic.query.get_or_404(id)
    if topic.parent is None:
        return Response("No se puede eliminar.", status=status.HTTP_303_SEE_OTHER)

    subtopics = Topic.query.filter_by(parent=topic)
    for subtopic in subtopics:
        db.session.delete(subtopic)

    db.session.delete(topic)
    db.session.commit()
    return Response(status=status.HTTP_200_OK)

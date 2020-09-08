from app.models import Project, Category, db
from app.forms import CategoryForm, CategoryUpdateForm
from flask import render_template, redirect, Response, Blueprint, jsonify, request, flash, g
from flask_login import login_required
from flask_api import status
import requests

# Define the blueprint: 'assets', set its url prefix: app.url/assets
bp = Blueprint('categories', __name__, url_prefix='/categories')


@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_category(project_id):
    """
    Creates a new category if there is not a category with given name.
    """
    project = Project.query.get_or_404(project_id)
    g.project = project
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, project=project)
        db.session.add(category)
        db.session.commit()
        return Response(status=status.HTTP_201_CREATED)

    if (form.errors):
        return render_template('categories/new_category.html', project=project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('categories/new_category.html', project=project, form=form), status.HTTP_200_OK


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """
    Allows user to edit an existing category.
    """
    category = Category.query.get_or_404(id)
    g.project = category.project
    form = CategoryUpdateForm()
    if form.validate_on_submit():
        category = Category.query.get_or_404(form.id.data)
        category.name=form.name.data
        db.session.commit()
        return redirect('/categories/{}'.format(category.id))
    
    if (form.errors):
        return render_template('categories/edit_category.html', category=category, project=category.project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('categories/edit_category.html', category=category, project=category.project, form=form)


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_category(id):
    """
    Allows user to delete an existing category.
    """
    category = Category.query.get_or_404(id)
    if (category is not None):
        db.session.delete(category)
        db.session.commit()
    return Response(status=status.HTTP_200_OK)


@bp.route('/<int:id>', methods=['GET'])
@login_required
def category(id):
    """
    Retrieve information about an existing category.
    """
    category = Category.query.get_or_404(id)
    return render_template('categories/category.html', project=category.project, category=category)

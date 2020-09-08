from flask import render_template, Response, Blueprint, redirect, current_app
from flask_login import login_required
from flask_api import status
from app import screenly_api
from app.models import Project, Client
import requests, io, logging

# Define the blueprint: 'general', set its url prefix: app.url/
bp = Blueprint('gral', __name__, url_prefix='/')


@current_app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@bp.route('/', methods=['GET'])
@login_required
def home():
    """
    Landing page.
    """
    projects = Project.query.count()
    if projects > 0:
        return redirect("/projects")
    return render_template('index.html')

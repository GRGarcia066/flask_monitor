from app.models import Project, Asset, Client, db
from app.forms import ClientForm, ClientUpdateForm
from app.schemas import client_schema, clients_schema, assets_schema
from flask import Response, redirect, render_template, jsonify, flash, \
    Blueprint, current_app, g
from flask_api import status
from flask_login import login_required
from app import screenly_api
import requests

# Define the blueprint: 'clients', set its url prefix: app.url /clients
bp = Blueprint('clients', __name__, url_prefix='/clients')


def parse_datetime(dtime):
    date_time = dtime.split("T")
    return "{} {}".format(date_time[0], date_time[1])

current_app.jinja_env.filters['datetime'] = parse_datetime


@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_client(project_id):
    """
    Allows user to creates a new screenly client.
    """
    project = Project.query.get_or_404(project_id)
    g.project = project
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(name=form.name.data, address=form.address.data, project=project, check_interval=30000)
        if form.username.data:
            client.username = form.username.data
        if form.password.data:
            client.password=form.password.data
        db.session.add(client)
        db.session.commit()
        return redirect('/projects/{}'.format(project.name))
        
    if form.errors:
        return render_template('clients/new_client.html', project=project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('clients/new_client.html', form=form, project=project)


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_client(id):
    """
    Allows user to delete an existing client.
    """
    client = Client.query.get_or_404(id)
    if (client is not None):
        db.session.delete(client)
        db.session.commit()
    return Response(status=status.HTTP_200_OK)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    """
    Retrieve information about a client.
    """
    client = Client.query.get_or_404(id)
    response = screenly_api.retrieve_assets(client)

    if (response.status_code == status.HTTP_200_OK):
        project = client.project
        return render_template('clients/edit_client.html', project=project, client=client, offline=0)    
    elif (response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR):
        flash('Ha habido un error al intentar acceder al cliente {}, con Ip: {}.'.format(client.name, client.address), 'error')
    elif (response.status_code == status.HTTP_408_REQUEST_TIMEOUT):
        flash('El cliente {}, con Ip: {} está desconectado.'.format(client.name, client.address), 'error')
    return redirect('/')


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_client(id):       
    client = Client.query.get_or_404(id)
    g.project = client.project
    form = ClientUpdateForm()
    if form.validate_on_submit():
        if form.name.data:
            client.name = form.name.data

        if form.address.data:
            client.address = form.address.data

        if form.check_interval.data:
            client.check_interval = form.check_interval.data * 1000

        client.username = form.username.data

        if client.password == form.oldpassword.data:
            client.password = form.password.data
        else:
            flash("La contraseña es incorrecta.", "error")
            return render_template('clients/update_client.html', client=client, form=form)

        db.session.commit()
        return Response(status=status.HTTP_200_OK)
         
    if form.errors:
        return render_template('clients/update_client.html', client=client, form=form), status.HTTP_303_SEE_OTHER

    return render_template('clients/update_client.html', client=client, form=form)


@bp.route('/<int:id>', methods=['GET'])
@login_required
def client(id):
    """
    Retrieve information about a client.
    """
    client = Client.query.get_or_404(id)
    offline = 1
    assets=[]

    response = screenly_api.retrieve_assets(client)
    if response.status_code == status.HTTP_200_OK:
        offline=0
        assets=response.json()
    return render_template('clients/client.html', project=client.project, client=client, offline=offline, assets=assets)


@bp.route('/assets/<int:id>', methods=['GET'])
@login_required
def get_client_assets(id):
    client = Client.query.get_or_404(id)
    return render_template('clients/client_assets.html', client=client)


@bp.route('/table/<int:id>', methods=['GET'])
@login_required
def get_assets_table(id):
    client = Client.query.get_or_404(id)
    offline = 1
    assets=[]

    response = screenly_api.retrieve_assets(client)
    if response.status_code == status.HTTP_200_OK:
        offline=0
        assets=response.json()
    return render_template('clients/assets_table.html', client=client, offline=offline, assets=assets)


@bp.route('/all_assets/<int:project_id>', methods=['GET'])
@login_required
def get_all_assets(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('clients/assets.html', project=project)


@bp.route('/display/<int:client_id>/<int:state>/<int:option>', methods=['POST'])
@login_required
def control_display(client_id, state, option):
    """
    Turn on or off screenly clients at specific address.
    """
    client = Client.query.get_or_404(client_id)
    response = screenly_api.turn_on_off(client, state, option)
    return Response(status=response.status_code)


@bp.route('/shutdown/<int:id>', methods=['POST'])
@login_required
def shutdown(id):
    """
    Shutdown the screenly clients at specific address.
    """
    client = Client.query.get_or_404(id)
    response = screenly_api.shutdown(client)
    return Response(status=response.status_code)


@bp.route('/reboot/<int:id>', methods=['POST'])
@login_required
def reboot(id):
    """
    Shutdown the screenly clients at specific address.
    """
    client = Client.query.get_or_404(id)
    response = screenly_api.reboot(client)
    return Response(status=response.status_code)


@bp.route('/json/<int:id>', methods=['GET'])
@login_required
def client_json(id):
    """
    Retrieve information about a client <JSON>.
    """
    client = Client.query.get_or_404(id)
    client_sch = client_schema.dump(client)

    assets = client.assets
    assets_sch = assets_schema.dump(assets)
    return jsonify([client_sch, assets_sch])


@bp.route('/json', methods=['GET'])
@login_required
def clients_json():
    """
    Retrieve information about all the clients as json.
    """
    clients = Client.query.all()
    clients_shc = clients_schema.dump(clients)
    return jsonify(clients_shc)

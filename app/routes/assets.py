from app.models import Project, Asset, Client, db
from app.forms import AssetForm, AssetUpdateForm
from flask import Response, request, redirect, send_from_directory, \
                  render_template, Blueprint, jsonify, current_app, g, flash
from flask_login import login_required
from flask_api import status
from werkzeug.utils import secure_filename
from app import screenly_api
import json, os, uuid, hashlib, codecs

# Define the blueprint: 'assets', set its url prefix: app.url/assets
bp = Blueprint('assets', __name__, url_prefix='/assets')


def get_date(dtime):
    date_time = dtime.split("T")
    return date_time[0]

def get_time(dtime):
    date_time = dtime.split("T")
    time = date_time[1].split(":")
    return "{}:{}".format(time[0], time[1])

current_app.jinja_env.filters['Date'] = get_date
current_app.jinja_env.filters['Time'] = get_time


def handle_errors(result):
    if result.status_code == status.HTTP_401_UNAUTHORIZED:
        return Response(status=result.status_code)
    if result.status_code == status.HTTP_408_REQUEST_TIMEOUT:
        return Response(status=result.status_code)
    if result.status_code == status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED:
        return Response(status=result.status_code)
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_asset(project_id):
    """
    Allows users to create a new assets.
    """
    project = Project.query.get_or_404(project_id)
    g.project = project
    form = AssetForm()  
    if form.validate_on_submit():
        f = form.upload.data
        asset_file = secure_filename(f.filename)

        file_name, file_extension = os.path.splitext(asset_file)

        # generates a unique asset id
        asset_id = str(uuid.uuid4())

        # get sha1 hash to generate a unique and valid path
        asset_filename = hashlib.sha1(asset_id.encode()).hexdigest() + file_extension
        
        # save assets in local storage path
        path = current_app.config['UPLOAD_FOLDER']
        f.save(os.path.join(path, asset_filename))

        asset = Asset(id=asset_id, name=asset_file, filename=asset_filename, project=project)
        categories = form.category.data
        if categories is not None:
            for category in categories:
                asset.categories.append(category)
 
        db.session.add(asset)
        db.session.commit()
        return redirect('/projects/{}'.format(project.name))
                
    if form.errors:
        return render_template('assets/new_asset.html', project=project, form=form), status.HTTP_303_SEE_OTHER

    return render_template('assets/new_asset.html', project=project, form=form)


@bp.route('/<string:id>', methods=['DELETE'])
@login_required
def delete_asset(id):
    """
    Allows users to delete assets.
    """
    asset = Asset.query.get_or_404(id)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], asset.filename)
    if os.path.exists(path):
        os.unlink(path)

    db.session.delete(asset)
    db.session.commit()
    return Response(status=status.HTTP_200_OK)


@bp.route('/<string:id>', methods=['GET'])
@login_required
def asset(id):
    """
    Retrive information about especific asset.
    """
    asset = Asset.query.get_or_404(id)
    return render_template('assets/asset.html', project=asset.project, asset=asset)


@bp.route('/upload/<int:client_id>/<string:asset_id>', methods=['POST'])
@login_required
def upload_asset(client_id, asset_id):
    """
    Allows users to upload new assets.
    """
    client = Client.query.get_or_404(client_id)
    asset = Asset.query.get_or_404(asset_id)
    r = screenly_api.upload_asset(client_id, asset_id)
    if r.status_code == status.HTTP_200_OK:
        client.assets.append(asset)
        db.session.commit()
        return Response(status=status.HTTP_200_OK)
    else:
        return handle_errors(r) 


@bp.route('/update/<int:client_id>/<string:asset_id>', methods=['GET', 'POST'])
@login_required
def update_asset(client_id, asset_id):
    client = Client.query.get_or_404(client_id)
    form = AssetUpdateForm()
    if form.validate_on_submit():
        data = {
            "mimetype": form.mimetype.data,
            "is_enabled": int(form.is_enabled.data),
            "name": form.name.data,
            "start_date": "{}T{}.000Z".format(form.startdate.data, form.starttime.data),
            "end_date": "{}T{}.000Z".format(form.enddate.data, form.endtime.data),
            "duration": int(form.duration.data),
            "play_order": int(form.play_order.data),
            "nocache": int(form.nocache.data),
            "uri": form.uri.data,
            "skip_asset_check": int(form.skip_asset_check.data),
        }       
        r = screenly_api.update_asset(client, asset_id, data)
        if r.status_code == status.HTTP_200_OK:
            return redirect('/clients/{}'.format(client.id))
    else:
        r = screenly_api.get_asset(client, asset_id)
        if r.status_code == status.HTTP_200_OK:
            data = r.json()
            return render_template('assets/edit_asset.html', form=form, asset=data, project=client.project)          
    return handle_errors(r)


@bp.route('/<int:client_id>/<string:asset_id>', methods=['DELETE'])
@login_required
def delete_client_asset(client_id, asset_id):
    """
    Allows user to delete an existing asset.
    """
    asset = Asset.query.get(asset_id)
    client = Client.query.get_or_404(client_id)

    if asset is not None and asset in client.assets:
        client.assets.remove(asset)
        db.session.commit()

    # Delete asset from screenly client
    r = screenly_api.delete_asset(client, asset_id)
    if r.status_code == status.HTTP_204_NO_CONTENT:
        return Response("Asset eliminado."), status.HTTP_204_NO_CONTENT
    elif r.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        # if asset is deleted using screenly-ose page then api
        # will return error when trying to delete non existing asset
        return Response("Asset eliminado."), status.HTTP_200_OK
    else:
        return handle_errors(r)


@bp.route('/enable/<int:client_id>/<string:asset_id>', methods=['PUT'])
@login_required
def enable_client_asset(client_id, asset_id):
    """
    Allows user to enable/disable an existing asset.
    """
    client = Client.query.get_or_404(client_id)
    r = screenly_api.enable_asset(client, asset_id)
    if r.status_code == status.HTTP_200_OK:
        return Response(status=status.HTTP_200_OK)
    else:
        return handle_errors(r)


@bp.route('/control/<int:client_id>/<string:command>', methods=['POST'])
@login_required
def control_asset(client_id, command):
    client = Client.query.get_or_404(client_id)
    r = screenly_api.control_asset(client, command)
    if r.status_code == status.HTTP_200_OK:
        return Response(status=status.HTTP_200_OK)
    else:
        return handle_errors(r)


@bp.route('/screenshot/<int:client_id>', methods=['GET'])
@login_required
def get_screenshot(client_id):
    client = Client.query.get_or_404(client_id)
    r = screenly_api.get_screenshot(client)
    if r.status_code == status.HTTP_200_OK:
        base64_data = codecs.encode(r.content, 'base64')
        base64_text = codecs.decode(base64_data, 'ascii')
        return jsonify(base64_text, status.HTTP_200_OK)
    else:
        return handle_errors(r)


@bp.route('/uploads/<string:filename>')
def uploaded_file(filename):
    folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(folder, filename)

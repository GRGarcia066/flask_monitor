from flask import Blueprint, render_template, redirect, Response, g
from flask_login import login_required
from flask_api import status
from app.models import Project, Subscription
from app.mqtt import mqtt_client, mqtt_controls
from app.forms import MQTTSettingsForm, MQTTCredentials
from flask import current_app as app
from werkzeug.utils import secure_filename
import os

# Define the blueprint: 'mqtt', set its url prefix: app.url /mqtt
bp = Blueprint('mqtt', __name__, url_prefix='/mqtt')


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Mqtt settings.
    """
    form = MQTTSettingsForm()
    if form.validate_on_submit():
        app.config['MQTT_CLIENT_ID'] = form.client_id.data 
        app.config['MQTT_BROKER_ADDRESS'] = form.broker_address.data  
        app.config['MQTT_BROKER_PORT'] = form.broker_port.data
        app.config['MQTT_CONNECTION_TIMEOUT'] = form.connection_timeout.data
        app.config['MQTT_KEEP_ALIVE_INTERVAL'] = form.keep_alive_interval.data
        app.config['MQTT_USE_HTTP_PROXY'] = form.use_proxy.data
        # app.config['MQTT_VERSION'] = form.version.data
        app.config['MQTT_TLS_PROTOCOL'] = form.tls_protocol.data
        app.config['MQTT_PROXY_HOST'] = form.proxy_host.data
        app.config['MQTT_PROXY_PORT'] = form.proxy_port.data
        app.config['MQTT_START_ON_LAUNCH'] = "1" if form.start_on_launch.data else "0"
        app.config['MQTT_CLEAN_SESSION'] = "1" if form.clean_session.data else "0"
        app.config['MQTT_AUTO_RECONNECT'] = "1" if form.auto_reconnect.data else "0"
        app.config['MQTT_SSL/TLS'] = "1" if form.secure.data else "0"
        app.config['MQTT_USE_HTTP_PROXY'] = "1" if form.use_proxy.data else "0"

        if form.ca_file_path.data:
            f = form.ca_file_path.data
            ca_file = secure_filename(f.filename)
            f.save(os.path.join('certs', ca_file))
            app.config['MQTT_CA_FILE_PATH'] = ca_file
            
        mqtt_client.update_settings(app)

    mqtt_settings = {}
    for key in app.config.keys():
        if (key.startswith('MQTT_')):
            mqtt_settings[key] = app.config[key]

    return render_template('settings/mqtt.html', form=form, mqtt_settings=mqtt_settings)


@bp.route('/credentials', methods=['GET', 'POST'])
@login_required
def credentials():
    """
    Mqtt credentials
    """
    form = MQTTCredentials()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        try:
            mqtt_client.username_pw_set(username=username,password=password)
            app.config['MQTT_PASSWORD_PROTECTED'] = "1"
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return render_template('settings/mqtt_credentials.html', form=form)


@bp.route('/<int:state>', methods=['POST'])
@login_required
def control_mqtt(state):
    """
    Mqtt control.
    """
    try:
        if state == 1:
            mqtt_client.start()
        else:
            mqtt_client.stop()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@bp.route('/controls/<int:control>/<int:project_id>', methods=['POST'])
@login_required
def control_subscriptions(control, project_id):
    """
    Starts or stops mqtt client and existing subscriptions.
    """
    project = Project.query.get_or_404(project_id) 
    if control == 0: # stop
        try:
            mqtt_client.unsubscribe_project(project)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif control == 1: # start
        subscriptions = Subscription.query.filter_by(project=project, status=1).all()

        try:
            mqtt_client.load_subscriptions(subscriptions)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif control not in mqtt_controls.keys():
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

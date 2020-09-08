from app import Config
from app.models import Client, Asset
from flask import Response, g
from flask_api import status
import requests, os, logging, datetime


requests.packages.urllib3.disable_warnings()
headers={ 'Cache-Control': 'no-cache' }


def handle_exceptions(e):
    logging.critical(e)
    if isinstance(e, requests.exceptions.ConnectTimeout):
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    elif isinstance(e, requests.exceptions.ReadTimeout):
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    elif isinstance(e, requests.exceptions.SSLError):
        return Response(status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
    elif isinstance(e, requests.exceptions.ConnectionError):
        return Response(status=status.HTTP_408_REQUEST_TIMEOUT)
    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def make_url(client_address, version, action=""):
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client_address + '/api/' + version + '/assets' + action
    else:
        url = "http://" + client_address + '/api/' + version + '/assets' + action 
    return url


def screenly_request(url, client, method, assetFile=None, assetInfo=None):

    auth=requests.auth.HTTPBasicAuth(client.username, client.password)
    
    try:
        if method == "GET":
            r = requests.get(url, timeout=Config.SCREENLY_CONNECTION_TIMEOUT, headers=headers, auth=auth, verify=False)
        elif method == "DELETE":
            r = requests.delete(url, timeout=Config.SCREENLY_CONNECTION_TIMEOUT, headers=headers, auth=auth, verify=False)
        elif method == "POST":
            r = requests.post(url, timeout=Config.SCREENLY_CONNECTION_TIMEOUT, files=assetFile, json=assetInfo, headers=headers, auth=auth, verify=False)     
        elif method == "PUT":
            r = requests.put(url, timeout=Config.SCREENLY_CONNECTION_TIMEOUT, json=assetInfo, headers=headers, auth=auth, verify=False)    

    except Exception as e:
        r = handle_exceptions(e)

    finally:
        return r



def get_current_asset(client, version = 'v1'):
    """
    Retrive information about currently running asset
    """
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + '/api/' + version + '/viewer_current_asset'
    else:
        url = "http://" + client.address + '/api/' + version + '/viewer_current_asset'
    return screenly_request(url, client, "GET")


def get_asset(client, asset_id, version = 'v1.2'):
    """
    Retrive information about specific asset by asset_id value
    """
    url = make_url(client.address, version, action="/{}".format(asset_id))
    return screenly_request(url, client, "GET")


def retrieve_assets(client, version = 'v1.2'):
    """
    Retrieve information about all assets
    """
    url = make_url(client.address, version)
    return screenly_request(url, client, "GET")


def delete_asset(client, asset_id, version = 'v1.2'):
    """
    Deletes screenly asset
    """
    url = make_url(client.address, version, action="/{}".format(asset_id))
    return screenly_request(url, client, "DELETE")


def upload_asset(client_id, asset_id):
    """
    This a 2 parts process, 
    first we send the asset to be stored in the raspberry   
    """ 
    client = Client.query.get(client_id)
    asset = Asset.query.get(asset_id)
    path = os.path.join(Config.UPLOAD_FOLDER, asset.filename)

    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + '/api/v1/file_asset'
    else:
        url = "http://" + client.address + '/api/v1/file_asset'
    
    try:
        asset_file = open(path, 'rb')
        assetFile = {'file_upload' : asset_file}
        r = screenly_request(url, client, "POST", assetFile)

        if r.status_code == status.HTTP_200_OK:
            if asset.is_image():
                mimetype = "image"
            elif asset.is_video():
                mimetype = "video"
            else:
                mimetype = "webpage"

            now = datetime.datetime.now()

            assetInfo = {
                "asset_id": asset.id,
                "name": asset.name,
                "uri": r.json(),
                "mimetype": mimetype,

                "start_date": "{}-{}-{}T{}:{}:00.000Z".format(now.year - 1, now.month, now.day, 
                                                            now.hour, now.minute),

                "end_date": "{}-01-01T00:00:00.000Z".format(now.year + 1),
                "is_active": 0,
                "is_enabled": 0,
                "is_processing": 0,
                "nocache": 0,
                "play_order": 0,
                "skip_asset_check": 0
            }

            # Screenly handles video duration when 0 is received
            if mimetype == "video":
                assetInfo['duration'] = 0
            else:
                assetInfo['duration'] = Config.SCREENLY_ASSET_DEFAULT_DURATION

            r = create_asset(client, assetInfo)
    
    except Exception as e:
        r = handle_exceptions(e)

    finally:
        if isinstance(r, Response):
            return r
        return Response(r)


def create_asset(client, assetInfo):
    """
    Then tell screenly to add a new asset and where it is located
    """
    url = make_url(client.address, version='v1.1')
    r = screenly_request(url, client, "POST", assetInfo=assetInfo)

    if r.status_code == status.HTTP_201_CREATED:
        url = make_url(client.address, version='v1', action="/order")
        return screenly_request(url, client, "POST", assetInfo={"ids": ""})
    return Response(status=r.status_code)


def update_asset(client, asset_id, assetInfo, version = 'v1.2'):
    """
    Allows user to update any asset value
    """
    url = make_url(client.address, version, action="/{}".format(asset_id))
    return screenly_request(url, client, "PUT", assetInfo=assetInfo)


def enable_asset(client, asset_id, version = 'v1.2'):
    """
    Allows user to enable/disable asset with given id
    """
    r = get_asset(client, asset_id)
    if r.status_code == status.HTTP_200_OK:
        data = r.json()
        enabled = data['is_enabled']
        active = data['is_active']
        if active == 1 or enabled == 1:
            data['is_active'] = 0
            data['is_enabled'] = 0
        else:
            data['is_active'] = 1      
            data['is_enabled'] = 1      
        return update_asset(client, asset_id, data, version)
    return r


def control_asset(client, command):
    '''
    Allows user to switch assets
    '''
    url = make_url(client.address, version='v1', action="/control/{}".format(command))
    return screenly_request(url, client, "GET")


def get_screenshot(client, version = 'v1'):
    '''
    Allows user to get currently displaying asset
    '''
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + "/api/" + version + "/screenshot"
    else:
        url = "http://" + client.address + "/api/" + version + "/screenshot"
    return screenly_request(url, client, "GET")


def turn_on_off(client, state, option = 0, version = 'v1'):
    '''
    Allows user to turn on/off the display
    '''
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + "/api/" + version + "/display/{}/{}".format(state, option)
    else:
        url = "http://" + client.address + "/api/" + version + "/display/{}/{}".format(state, option)
    return screenly_request(url, client, "GET")


def shutdown(client, version='v1'):
    '''
    Allows user to shutdown the screenly client
    '''
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + "/api/" + version + "/shutdown_screenly"
    else:
        url = "http://" + client.address + "/api/" + version + "/shutdown_screenly"
    return screenly_request(url, client, "POST")


def reboot(client, version='v1'):
    '''
    Allows user to reboot the screenly client
    '''
    if Config.SCREENLY_SECURE_CONNECTION:
        url = "https://" + client.address + "/api/" + version + "/reboot_screenly"
    else:
        url = "http://" + client.address + "/api/" + version + "/reboot_screenly"
    return screenly_request(url, client, "POST")

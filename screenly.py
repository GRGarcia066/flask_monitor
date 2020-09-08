from app import create_app
from app.models import Asset, Client, Category, db
from config import Config
import logging, os


logging.basicConfig(level=logging.DEBUG)
if not os.path.exists('certs'):
    os.mkdir('certs')


logging.basicConfig(level=logging.DEBUG)
if not os.path.exists('logs/mqtt.log'):
    os.mkdir('logs')


fileHandler = logging.FileHandler('logs/mqtt.log')
fileHandler.setLevel(logging.CRITICAL)
logging.getLogger().addHandler(fileHandler)


path = Config.UPLOAD_FOLDER
if not os.path.exists(path):
    os.mkdir(path)


myapp = create_app()


@myapp.shell_context_processor
def make_shell_context():
    return {'db': db, 'Client': Client, 'Asset': Asset, 'Category': Category}


if not os.path.exists(Config.SERVER_CERT_PATH) or not os.path.exists(Config.SERVER_KEY_PATH):
    myapp.run(debug=Config.DEBUG, use_reloader=False, host='0.0.0.0', port='5000')
else:
    ssl_context = (Config.SERVER_CERT_PATH, Config.SERVER_KEY_PATH)
    myapp.run(ssl_context=ssl_context, debug=Config.DEBUG, use_reloader=False, host='0.0.0.0', port='5000')

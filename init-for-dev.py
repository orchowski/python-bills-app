import logging

from flask import Flask, send_from_directory
from flask_scss import Scss

from application.authentication.auth_model import User
from application.factory import ApplicationFactory
from infrastructure.logger import init
from view.create_views import CreateViewsFor

billApplication = Flask(__name__,
                        static_folder='templates/assets')
logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
init(billApplication.logger)
Scss(billApplication, asset_dir='templates/assets',
     static_dir='templates/assets').update_scss()

billApplication.config['DEBUG'] = True


@billApplication.route('/favicon.ico')
def favicon():
    return send_from_directory('templates/assets', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


CreateViewsFor(billApplication, ApplicationFactory())

if __name__ == '__main__':
    billApplication.run(debug=True, host='0.0.0.0')


@billApplication.before_first_request
def initDB():
    User.create_table()

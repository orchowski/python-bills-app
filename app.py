import logging
from datetime import date, datetime, timedelta

from flask import Flask, send_from_directory
from flask.json import JSONEncoder
from flask_scss import Scss

from application.factory import ApplicationFactory
from infrastructure.logger import init
from view.create_views import CreateViewsFor

dashMeMoneyApplication = Flask(__name__,
                               static_folder='templates/assets')
logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
init(dashMeMoneyApplication.logger)
Scss(dashMeMoneyApplication, asset_dir='templates/assets',
     static_dir='templates/assets').update_scss()

dashMeMoneyApplication.config['DEBUG'] = True

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if type(obj) == date:
                return obj.isoformat()
            if type(obj) == datetime:
                return obj.isoformat(timespec="seconds")
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)


dashMeMoneyApplication.json_encoder = CustomJSONEncoder


@dashMeMoneyApplication.route('/favicon.ico')
def favicon():
    return send_from_directory('templates/assets', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


CreateViewsFor(dashMeMoneyApplication, ApplicationFactory())

if __name__ == '__main__':
    dashMeMoneyApplication.run(debug=True, host='0.0.0.0')

import os
import time
import datetime

from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = 'v5cu42gs6g7tfgg'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_pyfile("dev_settings.cfg")
app.app_context().push()

from data_blueprint import data
app.register_blueprint(data, url_prefix="/")

from utils_blueprint import utils
app.register_blueprint(utils, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8888)), debug=True)
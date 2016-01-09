from flask import Flask
from werkzeug import secure_filename


drtysnow = Flask(__name__)

# imports configuration options from config file
drtysnow.config.from_object('drtysnow.config')
from drtysnow import views

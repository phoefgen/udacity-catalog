from flask import Flask

coreshot = Flask(__name__)
from coreshot import views

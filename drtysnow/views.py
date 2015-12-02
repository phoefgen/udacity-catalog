from drtysnow import drtysnow
from flask import render_template


@drtysnow.route('/')
@drtysnow.route('/index')


def index():
    return render_template('index.html')

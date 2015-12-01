from coreshot import coreshot
from flask import render_template


@coreshot.route('/')
@coreshot.route('/index')


def index():
    return render_template('index.html')

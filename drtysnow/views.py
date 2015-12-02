from drtysnow import drtysnow
from flask import render_template

# Landing pages.

@drtysnow.route('/')
@drtysnow.route('/index')
def index():
    return render_template('index.html')

@drtysnow.route('/prelaunch')
def prelaunch():
    return "Pre-launch page Not implemented"


# Content Creation pages.

@drtysnow.route('<int:user_id>/modify_profile')
def register_user(user_id):
    return "Modify {}'s profile page Not implemented".format(user_id)

@drtysnow.route('/register_resort')
def register_resort():
    return "Register_resort Not implemented"

@drtysnow.route('/resorts/<string:resort_name>/new_run')
def new_run(resort_name):
    return "Adding runs to {} is not implemented yet.".format(resort_name)

@drtysnow.route('/resorts/<string:resort_name>/<sting:run_name>')
def run_rating(resort_name, run_name):
    return "Adding ratings to {} at {} is not yet implemented".format(run_name,
                                                                   resort_name)

@drtysnow.route('')

#View Content pages.
@drtysnow.route('/<int:user_id>/user')
def show_user(user_id):
    return "User profile for {} not implemented yet.".format(user_id)


@drtysnow.route('/<int:resort_id>/resort')
def show_resort(resort_id):
    return "Resort profile for {} not implemented yet".format(resort_id)

@drtysnow.route('/<int:resort_id>/<int:run_id>/show')
def show_run(resort_id, run_id):
    return "Resort profile for {} not implemented yet".format(resort_id)

def fourohfour():
    return "Page Not found."

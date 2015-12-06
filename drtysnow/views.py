from drtysnow import drtysnow
from flask import render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbconn import connect, create_user, create_resort, create_runs
from dbconn import create_reviews, update, delete
from dbsetup import Base, Resorts, Users, Runs, Reviews

#Connect to the database:
def connect():
    engine = create_engine('sqlite:///drtysnow/drtysnow.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    s = DBSession()
    return s

# Landing pages.
@drtysnow.route('/')
@drtysnow.route('/index')
def index():
    return render_template('cover.html')


@drtysnow.route('/landing')
def landing():
    return render_template('landing.html')

@drtysnow.route('/prelaunch')
def prelaunch():
    return "Pre-launch page Not implemented"


# Content Creation pages.

@drtysnow.route('/<int:user_id>/modify_profile')
def register_user(user_id):
    return "Modify {}'s profile page Not implemented".format(user_id)

@drtysnow.route('/register_resort')
def register_resort():
    return "Register_resort Not implemented"

@drtysnow.route('/resorts/<string:resort_name>/new_run')
def new_run(resort_name):
    return "Adding runs to {} is not implemented yet.".format(resort_name)

@drtysnow.route('/resorts/<string:resort_name>/<string:run_name>')
def run_rating(resort_name, run_name):
    return "Adding ratings to {} at {} is not yet implemented".format(run_name,
                                                                   resort_name)

#View Content pages.

@drtysnow.route('/profile/<int:user_id>')
def show_user(user_id):
    engine = create_engine('sqlite:///drtysnow.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    s = DBSession()

    result = s.query(Users).first()
    return result.first_name




@drtysnow.route('/resort/<int:resort_id>')
def show_resort(resort_id):

    return "Resort profile for {} not implemented yet".format(resort_id)

@drtysnow.route('/run/<int:resort_id>/<int:run_id>')
def show_run(resort_id, run_id):
    return "Run profile for {} not implemented yet".format(resort_id)

@drtysnow.route('/fourohfour')
def fourohfour():
    return "Page Not found."

def main():
    # test db connection
    s = connect()
    print s



if __name__ == '__main__':
    main()

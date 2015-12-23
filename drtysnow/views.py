from drtysnow import drtysnow
from flask import render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.dbconn import connect, create_user, create_resort, create_runs
from db.dbconn import create_reviews, update, delete
from db.dbsetup import Base, Resorts, Users, Runs, Reviews


# Landing pages.
@drtysnow.route('/')
@drtysnow.route('/index')
def index():
    return render_template('pre_login/cover.html')


@drtysnow.route('/landing')
def landing():
    return render_template('pre_login/landing.html')

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
    '''
    Takes an integer from the URL, and populates a profile page for the
    user with the same ID in the users table.
    '''
    # Get basic user details.
    profile_result = connect().query(Users).get(user_id)
    profile_details = profile_result.__dict__

    #translate resort ID into resort string.
    resort_result = connect().query(Resorts).get(
                                         profile_details['favourite_resort_id'])
    resort_details = resort_result.__dict__

    #Generate a list of dict's with reviews by user.
    reviews_result = connect().query(Reviews).filter_by(
                                                        user_id = user_id).all()
    review_list = []
    for review in reviews_result:
        # convert run id to resort name:
        resort_id  = connect().query(Runs).get(review.run_id).resort_id
        resort_name = connect().query(Resorts).get(resort_id).resort_name

        r = {}
        r["resort_name"] = resort_name
        r["run_name"] = connect().query(Runs).get(review.run_id).run_name
        r["rating"] = review.rating
        r["comments"] = review.comments
        review_list.append(r)

    return render_template('profile/show_profile.html',
                               fname = profile_details['first_name'],
                               lname = profile_details['last_name'],
                               email = profile_details['email_address'],
                               favourite_resort = resort_details['resort_name'],
                               reviews = review_list)

@drtysnow.route('/resort/<int:resort_id>')
def show_resort(resort_id):
    '''
    Generates a profile page for the given resort, with a summary of all Runs
    '''

    # Get details abou the specified resort:
    resort_details = connect().query(Resorts).get(resort_id).__dict__

    # Get details about runs on the specified resort:
    run_details = connect().query(Runs).filter_by(resort_id = resort_id).all()

    return render_template('profile/show_resort.html',
                            resort_name = resort_details["resort_name"],
                            runs = run_details)

@drtysnow.route('/run/<int:run_id>')
def show_run(run_id):
    '''
    Present all details for a specified run.
    '''
    run_summary = []
    run_reviews = connect().query(Reviews).filter_by(run_id = run_id).all()
    run_name = connect().query(Runs).get(run_id).run_name

    for review in run_reviews:
        r = {}
        r["rating"] = review.rating
        r["comments"] = review.comments
        r["top_hazard"] = review.top_hazard
        r["mid_hazard"] = review.top_hazard
        r["bot_hazard"] = review.bot_hazard
        run_summary.append(r)

    return render_template('profile/show_run.html',
                          run_name = connect().query(Runs).get(run_id).run_name,
                          run_summary = run_summary)

@drtysnow.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

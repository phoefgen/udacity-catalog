import datetime
from drtysnow import drtysnow
from flask import render_template, flash, redirect, url_for, request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.dbconn import connect, create_user, create_resort, create_run
from db.dbconn import create_reviews, update, delete
from db.dbsetup import Base, Resorts, Users, Runs, Reviews

from .forms.forms import ReviewRun, CreateResort, CreateRun
################################################################################
# Landing pages.
################################################################################

@drtysnow.route('/')
@drtysnow.route('/index')
def index():
    '''
    First page that users hit, after logging into the system. Restricted to
    users and admins only.
    '''
    return render_template('pre_login/cover.html')


@drtysnow.route('/landing')
def landing():
    '''
    Handle users that are not logged in, who initially encounter the site.
    '''
    return render_template('pre_login/landing.html')

@drtysnow.route('/prelaunch')
def prelaunch():
    '''
    Returns a teaser page. This is so the site can be hosted on the public
    internet and log traffic, but not be actually accessable during development.
    '''
    return "Pre-launch page Not implemented"

################################################################################
# Content Creation pages.
################################################################################

@drtysnow.route('/<int:user_id>/modify_profile')
def register_user(user_id):
    '''
    Return a form, to allow a non-user to enter a new resort, and then process
    the results of the form.
    '''
    return "Modify {}'s profile page Not implemented".format(user_id)

@drtysnow.route('/register_resort/', methods=['GET', 'POST'])
def register_resort():
    '''
    Return a form, to allow an administrator to enter a new resort, and then
    process the results of the form.
    '''
    form = CreateResort()

    # Check to see if form data is valid. If not, render template
    # if so, write the form data to the database, and prompt to enter
    # another resort.

    if form.validate_on_submit():
        name = str(form.name.data)
        location = str(form.location.data)
        summary = str(form.summary.data)
        c = connect()
        create_resort(c, name, location, summary)
        flash('Successfully added {0}!'.format(name))
        return redirect('/resort/{0}'.format(name))

    return render_template('create/new_resort.html',form=form)


@drtysnow.route('/resort/<string:resort_name>/new_run',
                                                        methods=['GET', 'POST'])
def new_run(resort_name):
    '''
    Return a form, to allow an administrator to enter a new ski run to an
    existing resort, and then process the results of the form.
    '''
    # Translate the URL to a resort primary key. Resort names are guaranted
    # unique:
    resort_key = (connect().query(Resorts)
                               .filter_by(resort_name = resort_name).first()).id

    form = CreateRun()

    # Check to see if form data is valid. If not, render template
    # if so, write the form data to the database, and prompt to enter a new
    # run on the same resort.

    if form.validate_on_submit():
        run_name = str(form.name.data)
        summary = str(form.summary.data)
        image = str(form.image.data)

        c = connect()
        create_run(c, run_name, resort_key, summary)
        flash('Successfully added {0} to {1}'.format(run_name, resort_name))
        return redirect('/resort/{0}'.format(resort_name))

    return render_template('create/new_run.html',
                            resort_name=resort_name,
                            form=form)


@drtysnow.route('/resort/review/<string:resort_name>/<int:run_id>/new',
                                                        methods=['GET', 'POST'])
def run_review(resort_name, run_id):
    '''
    Return a form, to allow the user to enter a new review of a ski run, and then
    process the results of the form.
    '''
    form = ReviewRun()

    if form.validate_on_submit():
        print "form valid"
        rating = int(form.rating.data)
        top_hazard = form.top_hazard.data
        mid_hazard = form.mid_hazard.data
        bot_hazard = form.bot_hazard.data
        comment = form.comment.data
        time = str(datetime.datetime.now().time())
        print 'parsed form'

        c = connect()
        n = create_reviews(c, run_id, rating, 5, top_hazard, mid_hazard, bot_hazard,
                                                            comment, time)
        flash('Successfully added review to {0}'.format(resort_name))
        print 'created review'
        return redirect('/resort/{0}/run/{1}'.format(resort_name, run_id))
    print "form not yet valid"
    print form.errors
    return render_template('create/new_review.html',
                            resort_name = resort_name,
                            run_id = run_id,
                            form = form)






################################################################################
#View Content pages.
################################################################################

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

@drtysnow.route('/resort/<string:resort_name>')
def show_resort(resort_name):
    '''
    Generates a profile page for the given resort, with a summary of all Runs
    '''
    print resort_name
    # Translate the URL to a resort primary key:
    resort_id = (connect().query(Resorts)
                              .filter_by(resort_name = str(resort_name)).first()).id

    # Get details about the specified resort:
    resort_details = connect().query(Resorts).get(resort_id).__dict__

    # Get details about runs on the specified resort:
    run_details = connect().query(Runs).filter_by(resort_id = resort_id).all()

    return render_template('profile/show_resort.html',
                            resort_name = resort_details["resort_name"],
                            resort_summary = resort_details["resort_summary"],
                            resort_location =resort_details["resort_location"],
                            runs = run_details)

@drtysnow.route('/resort/<string:resort_name>/run/<int:run_id>')
def show_run(run_id, resort_name):
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
                          run_summary = run_summary,
                          run_id = run_id,
                          resort_name = resort_name)

@drtysnow.route('/resorts')
def show_all_resorts():
    '''
    Display all registered resorts.
    '''
    resorts = connect().query(Resorts).all()
    resort_brief = []

    for resort in resorts:
        r = {}
        r["resort_name"] = resort.resort_name
        r["resort_summary"] = resort.resort_summary
        r["image"] = resort.resort_image
        r["resort_location"] = resort.resort_location
        resort_brief.append(r)

    return render_template('profile/show_all_resorts.html',
                          all_resorts = resort_brief)

@drtysnow.route('/find_run')
def find_run():
    '''
    Start the run review process. Select a resort, then a run, then go to
    the run review page.
    '''

    resorts = connect().query(Resorts).all()
    names = []

    for resort in resorts:
        names.append(resort.resort_name)

    return render_template('profile/select_run.html', resorts=names)

################################################################################
# Utility Views.
################################################################################

@drtysnow.errorhandler(404)
def page_not_found(e):
    '''
    Handle broken links, and badly guessed links.
    '''

    return render_template('error/404.html'), 404

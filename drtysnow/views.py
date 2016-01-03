# Generic Python Classes:
import datetime, random, string, httplib2, json, requests

# Flask Classes:
from drtysnow import drtysnow
from flask import render_template, flash, redirect, url_for, request
from flask import session as login_session
from flask import make_response

# DB Classes:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Custom DB classes:
from db.dbconn import connect, create_user, create_resort, create_run
from db.dbconn import create_reviews, update, delete
from db.dbsetup import Base, Resorts, Users, Runs, Reviews

# WTForms models:
from .forms.forms import ReviewRun, CreateResort, CreateRun

# Auth Classes:
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Settings:
CLIENT_ID= json.loads(open('drtysnow/client_secrets.json', 'r').read())['web']['client_id']
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
    Return a form, to allow a user to change there profile options, and then
     process the results of the form.
    '''
    return "Modify {}'s profile page Not implemented".format(user_id)

@drtysnow.route('/register_resort/', methods=['GET', 'POST'])
def register_resort():
    '''
    Return a form, to allow an administrator to enter a new resort, and then
    process the results of the form.
    '''
    # Restrict content to admins.
    if need_login('admin'):
        return redirect('/login')

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
    # Restrict content to admins.
    if need_login('admin'):
        return redirect('login')

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
    Return a form, to allow a user to enter a new review of a ski run, and then
    process the results of the form.
    '''
    # Restrict content to registered users.
    if need_login('user'):
        return redirect('login')

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

@drtysnow.route('/new_user', methods=['GET', 'POST'])
def new_user():
    '''
    Return a user signup form, and process the results into the database.
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


################################################################################
#View Content pages.
################################################################################

@drtysnow.route('/profile/<int:user_id>')
def show_user(user_id):
    '''
    Takes an integer from the URL, and populates a profile page for the
    user with the same ID in the users table.
    '''
    # restrict content to registered users.
    if need_login('user'):
        return redirect('login')

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
    # Restrict content to registered users.
    if need_login('none'):
        user = False

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
# Login Handling.
################################################################################

@drtysnow.route('/login')
def login():
    '''
    generate and store session token:
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32))
    login_session['state'] = state
    return render_template('/pre_login/login.html', STATE=state)

@drtysnow.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    Do most of the heavy lifting for oauth with google:
    1) Check for session spoofing
    2) Request and then verify the data from the google api endpoint.
    3) Pull basic user data from google.
    4) handle and log errors.
    '''
    if request.args.get('state') !=login_session['state']:
        print 'state check failed'
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # convert the auth code into a credential object.
        oauth_flow = flow_from_clientsecrets('drtysnow/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the auth code.'),
                                                                            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check token:
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Check the result for the outcome:
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify the token from google:
    gplus_id = credentials.id_token['sub']
    print result
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Tokens ID doesnt match user ID."),
                                                                            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Match token to ensure the correct app is in use
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token does not match application"),
                                                                            401)
        print "Token does not match application"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check for exisiting login session:
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                                                            200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Now we have a verified, and stored session, pull user data:
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    # store the pulled details in the session object:
    login_session['username'] = data['name']
    login_session['last_name'] = data['family_name']
    login_session['first_name'] = data['given_name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['access_token'] = access_token

    # check to see if this is a new user, if it is, create a new user account:
    user_check()

    # provide feedback to the user:
    flash('{0}, you are now logged in.'.format(login_session['username']))
    return redirect('/landing')

@drtysnow.route('/gdisconnect')
@drtysnow.route('/logout')
def gdisconnect():
    '''
    Tear down the connection to google, and destroy all the session data. Return
    the user to a "pre-signin" state.
    '''

    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['last_name']
        del login_session['first_name']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


@drtysnow.route('/fbconnect', methods = ['POST'])
def fbconnect():
    # check for forgeries:
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state paramater'), 401)
        response.headers['Content-Type'] = 'application/json'
        return resonse
    access_token = request.data
    print "access token: " + access_token

    # upgrade token from single use for auth flow, to stateful session token:
    # Construct URL for this session:
    app_id = json.loads(
                    open('drtysnow/fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
                open('drtysnow/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?\
                                            grant_type=fb_exchange_token\
                                            &client_id=%s\
                                            &client_secret=%s\
                                            &fb_exchange_token=%s\
                                            ' % (app_id,app_secret,access_token)
    # Pull session specific data:
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user data:
    userinfo_url = "https://graph.facebookcom/v2.2/me"
    # remove expire tag from token:
    token = result.split("&")[0]

    # Pull user data, store in login session:
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['username'] = data['name']
    login_session['first_name'] = login_session['username'].split()[0]
    login_session['last_name'] = login_session['username'].split()[1]
    login_session['email'] = data['email']
    login_session['user_id'] = data['id']

    #Get User Pic URL:
    url = 'https://graph.facebook.com/v2.2/me/picture?%s\
                                                      &redirect=0\
                                                      &height=200\
                                                      &width=200' % token
    h = httplib2.http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # check to see if this is a new user, if it is, create a new user account:
    user_check()

    # provide feedback to the user:
    flash('{0}, you are now logged in.'.format(login_session['username']))
    return redirect('/landing')


################################################################################
# Error Handling.
################################################################################

@drtysnow.errorhandler(404)
def page_not_found(e):
    '''
    Handle broken links, and badly guessed links.
    '''

    return render_template('error/404.html'), 404


################################################################################
# Helper Functions:
################################################################################


def need_login(user_type):
    '''
    Verify user status, and differentiate between a user, a visitor, and an
    admin.
    '''
    # Check to see if this is a get request. Client will need to make a valid
    # GET request before they can make a POST request. The CSRF field drops all
    # non-authenticated form requests:
    if request.method == 'GET' and (user_type == 'admin' or user_type == 'user'):
        if 'username' not in login_session:
            flash('This content only available for registered {type}s. \
                                          Please login.'.format(type=user_type))
            return True
    return False

def user_check():
    '''
    After a user has been authenticated with an oauth provider, check to see if
    they are known to the site, create new user account if not.
    '''

    # check to see if a user exists in the database. Use email as a key, so that
    # a user account is persistent across oauth providers.
    if (connect().query(Users).filter_by(
                                 email_address = login_session['email']).first()):
        print 'User already exists'
        return True

    # This is a new user, create profile entry in database. Process user data.
    # there are other user options, these can be modified from the modify form
    # after user creation.
    first_name = login_session['first_name']
    last_name = login_session['last_name']
    email_address = login_session['email']
    administrator = False # All users are non-admins, unless explicity added.
    user_id = login_session['gplus_id']

    # create new user in local db with collected data:
    create_user(connect(), first_name,
                            last_name,
                            0,
                            administrator,
                            email_address,
                            user_id)

    print "created new user: {0}".format(login_session['username'])

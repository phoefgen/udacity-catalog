################################################################################
''' Define the data models for form processing'''
# Handling routing and page generation for the flask app.
#
# Author: Paul Hoefgen
################################################################################

# Generic Python Classes:
import datetime, random, string, httplib2, json, requests, os

# Flask Classes:
from drtysnow import drtysnow
from flask import render_template, flash, redirect, url_for, request
from flask import make_response, send_from_directory, jsonify
from flask import session as login_session

# DB Classes:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Custom DB classes:
from db.dbconn import connect, create_user, create_resort, create_run
from db.dbconn import create_reviews, delete
from db.dbsetup import Base, Resorts, Users, Runs, Reviews

# WTForms models:
from .forms.forms import ReviewRun, CreateResort, CreateRun, UpdateProfile, UpdateRun

# Auth Classes:
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Upload handling:
from werkzeug import secure_filename
from config import UPLOAD_FOLDER
# Settings:
CLIENT_ID= json.loads(open('/var/www/drtysnow/drtysnow/client_secrets.json', 'r').read())['web']['client_id']

################################################################################
# Landing pages.
################################################################################

@drtysnow.route('/')
@drtysnow.route('/index')
@drtysnow.route('/landing')

def index():
    '''
    First page that users hit, after logging into the system. Content adapts to
    logged in and unknown clients.
    '''
    return render_template('pre_login/landing.html')



################################################################################
# Content Creation pages.
################################################################################

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
    # if so, write the form data to the database, and display new resort profile
    if form.validate_on_submit():
        name = str(form.name.data)
        location = str(form.location.data)
        summary = str(form.summary.data)

        # process image to local storage:
        filename = name.replace(' ', '_')
        filename = filename + '_resort_pic.jpg'
        picture_path = os.path.join(drtysnow.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(picture_path)

        c = connect()
        create_resort(c, name, location, summary, picture_path)
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
        n = create_reviews(c, run_id, rating, login_session['id'], top_hazard, mid_hazard, bot_hazard,
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
# Edit Pages.
################################################################################

@drtysnow.route('/edit/profile/<int:user_id>', methods=['GET','POST'])
def edit_profile(user_id):
    '''
    Allow authorised clients to edit user profiles.
    '''

    # only allow admins and the user to edit profiles. Prompt non-authed users
    # to login, make sure that only the user can edit the profile:
    if 'id' in login_session:
        if (login_session['id'] == user_id) or (login_session['admin']):
            # Generate form obj:
            form = UpdateProfile()

            # Generate a form with the list of resorts:

            # pull list of resort names from the DB:
            resort_tuples = connect().query(Resorts.resort_name).all()
            # strip out the tuples, convert the unicode to strings:
            resort_unicode = [','.join(item) for item in resort_tuples]
            resort_list = []
            for i in resort_unicode:
                resort_list.append(str(i))

            # rebuild the resort list into a list of tuplesfor WTForms to
            # consume:
            resort_choices = []
            for resort in resort_list:
                choice = (resort, resort)
                resort_choices.append(choice)

            form = UpdateProfile()
            form.favorite_resort.choices = resort_choices

            # if this is a valid POST request, process the contents (referencing
            # the valid list of choices created above). Convert the data to
            # match The db, and then commit the changes:

            if form.validate_on_submit():
                favorite_resort = form.favorite_resort.data
                fav_id = int(connect().query(Resorts.id).filter_by(
                                      resort_name = favorite_resort).first()[0])
                conn = connect()
                change = conn.query(Users).filter_by(id = login_session['id']
                                                                       ).first()
                change.favourite_resort_id = fav_id
                change.administrator = form.is_admin.data
                conn.commit()
                flash('Submitted profile changes, logging out.')
                return redirect('/logout')
            return render_template('/edit/edit_profile.html', form=form)
        else:
            return reunder_template('/error/access_denied.html')
    else:
        return redirect('/login')

@drtysnow.route('/edit/run/<int:run_id>', methods=['GET','POST'])
def edit_run(run_id):
    '''
    Allow Autorised clients to edit ski runs
    '''

    # only allow admins  edit run profiles. Prompt non-authed users
    # to login, make sure that only the user can edit the profile:
    if 'id' in login_session:
        if (login_session['admin']):
            form = UpdateRun()

            # handle a valid form submission:
            # if this is a valid POST request, process the contents:
            if form.validate_on_submit():
                # Grab data from form:
                new_name = form.run_name.data
                new_description = form.run_description.data
                # Push it into the db:
                conn = connect()
                change = conn.query(Runs).filter_by(id = run_id).first()
                change.run_name = new_name
                change.run_description = new_description
                conn.commit()
                # push the changes, then show the new run profile:
                return redirect('/resort/edited/run/{0}'.format(run_id))

            # if this is not a valid POST, return a pre-populated field:
            run_name = connect().query(Runs).get(run_id).run_name
            run_description = connect().query(Runs).get(run_id).run_description
            form.run_name.data = run_name
            form.run_description.data = run_description
            return render_template('/edit/edit_run.html', form=form,
                                                          run_id = run_id)

        else: # Block non-admins from editing:
            return render_template('/error/access_denied.html')
    else: # Force login before considering user:
        return redirect('/login')

@drtysnow.route('/edit/resort/<int:resort_id>', methods=['GET','POST'])
def edit_resort(resort_id):
    '''
    Allow authorised clients to edit resort details
    '''

    # only allow admins  edit resorts. Prompt non-authed users
    # to login, make sure that only the user can edit the profile:
    if 'id' in login_session:
        if (login_session['admin']):
            form = CreateResort()

            # handle a valid form submission:
            # if this is a valid POST request, process the contents:
            if form.validate_on_submit():
                # Grab data from form:
                new_name = form.name.data
                new_summary = form.summary.data
                new_location = form.location.data

                # Push it into the db:
                conn = connect()
                change = conn.query(Resorts).filter_by(id = resort_id).first()

                change.resort_name = new_name
                change.resort_summary = new_summary
                change.resort_location = new_location

                # get the url, either from the db if it hasnt been changed, or
                # from the form if it has been changed:
                redirect_name = change.resort_name

                # check to see if a new image was uploaded:
                if form.image.data:
                    # Save the image to the local filesystem, set path for The
                    # db commit:
                    filename = redirect_name.replace(' ', '_')
                    filename = filename + '_resort_pic.jpg'
                    picture_path = os.path.join(drtysnow.config['UPLOAD_FOLDER'],
                                                                       filename)
                    form.image.data.save(picture_path)

                    change.resort_image = picture_path
                conn.commit()
                # push the changes, then show the new resort profile:
                return redirect('/resort/{0}'.format(redirect_name))

            # if this is not a valid POST, return a pre-populated field:
            resort_name = connect().query(Resorts).get(resort_id).resort_name
            resort_location = connect().query(Resorts).get(
                                                      resort_id).resort_location
            resort_summary = connect().query(Resorts).get(
                                                       resort_id).resort_summary

            form.name.data = resort_name
            form.summary.data = resort_summary
            form.location.data = resort_location
            return render_template('/edit/edit_resort.html', form=form,
                                                          resort_id = resort_id)

        else: # Block non-admins from editing:
            return render_template('/error/access_denied.html')
    else: # Force login before considering user:
        return redirect('/login')

@drtysnow.route('/delete/<string:del_type>/<int:primary_key>')
def delete_record(del_type, primary_key):
    '''
    Delete an arbitrary record based on URL and user permission:
    '''
    if del_type == 'Runs':
        # get resort ID for post-delete redirect:
        resort_int = connect().query(Runs).get(primary_key).resort_id
        resort_str = connect().query(Resorts).get(resort_int).resort_name

        # delete record from db:
        c = connect()
        delete_this = c.query(Runs).filter_by(id = primary_key).first()
        c.delete(delete_this)
        c.commit()
        return redirect('/resort/{0}'.format(resort_str))

    if del_type == 'Resorts':
        # delete resort from db:
        c = connect()
        delete_this = c.query(Resorts).filter_by(id = primary_key).first()
        c.delete(delete_this)
        c.commit()
        return redirect('/resorts')


################################################################################
#View Content pages.
################################################################################

@drtysnow.route('/profile/<int:user_id>')
def show_user(user_id):
    '''
    Takes an integer from the URL, and populates a profile page for the
    user with the same ID in the users table. Can also return JSON with the
    ?format='json'
    '''
    # restrict content to registered users.
    if need_login('user'):
        return redirect('login')

    # Get user details.
    profile_result = connect().query(Users).get(user_id)
    profile_details = profile_result.__dict__

    # if users favorite resort no longer exists (has been deleted from the db),
    # handle gracefully:
    try:
        #translate resort ID into resort string.
        resort_result = connect().query(Resorts).get(
                                             profile_details['favourite_resort_id'])
        resort_details = resort_result.__dict__
    except:
        resort_details = 'Not Found'

    #Generate a list of dict's with reviews by user.
    reviews_result = connect().query(Reviews).filter_by(
                                                        user_id = user_id).all()
    review_list = []
    for review in reviews_result:
        try:# if any data has been deleted, skip.
            # convert run id to resort name:
            resort_id  = connect().query(Runs).get(review.run_id).resort_id
            resort_name = connect().query(Resorts).get(resort_id).resort_name

            r = {}
            r["resort_name"] = resort_name
            r["run_name"] = connect().query(Runs).get(review.run_id).run_name
            r["rating"] = review.rating
            r["comments"] = review.comments
            review_list.append(r)
        except:
            continue

    # Return JSON if requested:
    if request.args.get('format') == 'json':
        del profile_details['_sa_instance_state']
        return jsonify(**profile_details)

    # if not an API Call, render page pending available data discovered earlier.
    try:
        return render_template('profile/show_profile.html',
                                   fname = profile_details['first_name'],
                                   lname = profile_details['last_name'],
                                   email = profile_details['email_address'],
                                   favourite_resort = resort_details['resort_name'],
                                   reviews = review_list,
                                   picture = profile_details['user_picture'])
    except: # handle the previous exception catch:
        return render_template('profile/show_profile.html',
                                   fname = profile_details['first_name'],
                                   lname = profile_details['last_name'],
                                   email = profile_details['email_address'],
                                   favourite_resort = 'Not Found',
                                   reviews = review_list,
                                   picture = profile_details['user_picture'])


@drtysnow.route('/resort/<string:resort_name>')
def show_resort(resort_name):
    '''
    Generates a profile page for the given resort, with a summary of all Runs.
    Returns JSON instead of HTML if 'format=json' is set in the URL.
    '''
    # Restrict content to registered users.
    if need_login('none'):
        user = False

    # Translate the URL to a resort primary key:
    resort_id = (connect().query(Resorts)
                          .filter_by(resort_name = str(resort_name)).first()).id

    # Get details about the specified resort:
    resort_details = connect().query(Resorts).get(resort_id).__dict__

    # Get details about runs on the specified resort:
    run_details = connect().query(Runs).filter_by(resort_id = resort_id).all()

    # Return JSON if requested:
    if request.args.get('format') == 'json':
        del resort_details['_sa_instance_state']
        return jsonify(**resort_details)

    return render_template('profile/show_resort.html',
                            resort_name = resort_details["resort_name"],
                            resort_summary = resort_details["resort_summary"],
                            resort_location =resort_details["resort_location"],
                            runs = run_details,
                            resort_pic = str(resort_details["resort_name"]
                                        ).replace(' ', '_') + '_resort_pic.jpg',
                            resort_id = resort_id)

@drtysnow.route('/resort/<string:resort_name>/run/<int:run_id>')
def show_run(run_id, resort_name):
    '''
    Present all details for a specified run.
    '''
    run_summary = []
    run_reviews = connect().query(Reviews).filter_by(run_id = run_id).all()
    run_name = connect().query(Runs).get(run_id).run_name
    run_description = connect().query(Runs).get(run_id).run_description

    for review in run_reviews:
        r = {}
        r["rating"] = review.rating
        r["comments"] = review.comments
        r["top_hazard"] = review.top_hazard
        r["mid_hazard"] = review.top_hazard
        r["bot_hazard"] = review.bot_hazard
        run_summary.append(r)

    # Return JSON if requested:
    if request.args.get('format') == 'json':
        run_return = {'run_name': run_name,
                       'run_id': run_id,
                       'resort_name': resort_name,
                       'run_description': run_description}
        return jsonify(**run_return)

    return render_template('profile/show_run.html',
                          run_name = run_name,
                          run_summary = run_summary,
                          run_id = run_id,
                          resort_name = resort_name,
                          run_description = run_description)

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
        r["image"] = str(resort.resort_name.replace(' ', '_')) + '_resort_pic.jpg'
        r["resort_location"] = resort.resort_location
        resort_brief.append(r)

    if request.args.get('format') == 'json':
        return jsonify({'all_resorts': resort_brief})

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
    generate and store session token.
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
        oauth_flow = flow_from_clientsecrets('/var/www/drtysnow/drtysnow/client_secrets.json', scope='')
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
    print 'User name is: ' + str(login_session['username'])
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['last_name']
        del login_session['first_name']
    	del login_session['email']
    	del login_session['picture']
        del login_session['id']
        del login_session['admin']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
        flash('Logged Out')
        return redirect('/landing')
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	flash('Failed to logout')
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
        # Add custom data from the local DB about this user session:
        login_session['id'] = connect().query(Users).filter_by(
                              email_address = login_session['email']).first().id
        login_session['admin'] = connect().query(Users).filter_by(
                             email_address = login_session['email']).first().administrator
        return True

    # This is a new user, create profile entry in database. Process user data.
    # there are other user options, these can be modified from the modify form
    # after user creation. ie, favourite resort.
    first_name = login_session['first_name']
    last_name = login_session['last_name']
    email_address = login_session['email']
    administrator = False    # users are non-admins, until escalated in the UI.
    user_id = login_session['gplus_id']
    picture = login_session['picture']

    # create new user in local db with collected data:
    create_user(connect(), first_name,
                            last_name,
                            0,
                            administrator,
                            email_address,
                            user_id,
                            picture)

    print "created new user: {0}".format(login_session['username'])

def list_resorts():
    '''
    Query the database for a list of all current resorts. Return a list that is
    formatted for consumption by WTForms
    '''
    resorts = connect().query(Resorts).all()
    names = []
    for resort in resorts:
        names.append('("{0}"),("{0}")'.format(resort.resort_name))

@drtysnow.route('/uploaded-images/<filename>')
def send_file(filename):
    path_to_images = os.path.join(drtysnow.root_path, 'data/resort_images')

    # return requested file if it exsits:
    if os.path.exists(path_to_images + '/' + filename):
        return send_from_directory(os.path.join(drtysnow.root_path,
                                                'data/resort_images'), filename)

    # degrade gracefully if file not found:
    return send_from_directory(os.path.join(drtysnow.root_path,
                                          'data/resort_images'), 'no_image.png')

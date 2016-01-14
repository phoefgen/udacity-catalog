## DRTYsnow

This repo is specifically been structured to comply with the Udacity FSND P3
Further dev work is continuing on this in https://github.com/phoefgen/drtysnow, however that repo should not
be considered in the scope of this submission. 

## Synopsis

A tool to monitor the realtime condition of inbound marked runs on ski resorts,
using user generated content. A Waze for skiing.

## Motivation

Snow conditions on ski runs change from hour to hour, and resort management is
rarely motivated to provide accurate and honest ski reports. Skiers and
snowboarders are in the best position to provide unbiased, constantly updated
information on the ever changing conditions, and potential hazards on ski runs.

## Installation

This is a flask app, with a sqlite3 database back end. Installation is currently
handled by Vagrant (requires Vagrant 1.5+).

change into the generated folder and then:
  'vagrant up'
  'vagrant ssh'

Vagrant will install all dependencies, and init the database. The setup includes
generating some lorem ipsum data to help with troubleshooting, assesment and dev.

If you want to reset the database, with test data run this shell script:
  'drtysnow/test_init.sh'

a new db file, without test data, can be generated and installed with:
  'python /vagrant/drtysnow/db/dbsetup.py'
  'mv /vagrant/drtysnow/db/drtysnow.py ../data'

Start the dev server with:
  'python run.py'


## Site Operation

A dev server runs in the vagrant box, serving files to the world from localhost port 5000.
Access the site with a web browser on the vagrant host.

  1) Dummy data is dumped at install.
  2) An unregistered user, can browse the site. An unregistered user cannot
     review ski runs, create resorts or runs, or view user details.
  3) Register via Google Oauth, this will create a local account and profile page.
     you will now be able to leave reviews on exists ski runs, and view your profile page.
  4) Edit your profile (settings menu) to escalate to an admin user. You may need to
     manually log out after this operation, and then log back in.
  5) You can check that you now have admin authority on the profile summary page.
     As an admin, new options will appear in place to edit, delete, and create all
     content including ski resorts, ski runs, etc.

The purpose of the website, is to read reviews and rate ski runs so that you can pick
the best place on the mountain to ski. At the top level there is a ski resort. A ski
resort contains a subset of ski paths, or runs, that have individual names. Each ski
run, has a subset of prior reviews for that run.

Ski resorts have an associated image with them. There is a single example image included
with the repo, and a placeholder image for resorts that dont have associated images.
Uploading an image (View Resort/Edit Resort) will update the image across the site.



## API Reference

A read only API is presented, that returns data in JSON format.

To view details on a specifc resort:
  <domain>:<port>/resort/<URL encoded resort%20name>?format=json

To view details on a specifc run:
  <domain>:<port>/resort/<URL encoded resort%20name>/run/<run id integer>?format=json

To view details of a specifc user:
  <domain>:<port>/profile/<user id integer>?format=json

To view a list of all resorts:
  <domain>:<port>/resorts/?format=json

## Addressing Rubrik Criteria:

This is a fairly large project, thats grown in scope beyond the initial Rubrik
to make things a little easier, here is a key to find relevant sections of code:

API Endpoints:
    All view functions return JSON. Add '?format=json' to any view URL to retrieve JSON.
    JSON is implemented inside the standard web view controllers.

CRUD Read:
    Read Category from DB (runs with sub reviews, or resorts with sub runs in this context).
    db is called drtysnow.db, and is autogenerated at install. Can be reinitialised. Images
    are read from the DB, which points to the local file system.
CRUD Create:
    A registered user can create reviews that are stored in the database.
    A registered admin can create reviews, new resorts, and new Runs. Images can be uploaded when
    creating a resort.
CRUD Update:
  All registered users can edit favourite resort, and admin status on the profile page.
  Admins can modify all fields on resorts and runs, including images.
CRUD Delete:
  Admins can delete everything they create (Runs, Reviews, and Resorts.). CSRF tokens are used for
  data protection.

OAuth:
  Users are created via Google Oauth. A user record is then stored locally, and authed users content (reviews) are associated with the person who made them. Also, there are 3 tiers of users (unknown, user, admin). These three levels all have different abilities on the site.

## Contributors

**Paul Hoefgen** paul.hoefgen at gmail.

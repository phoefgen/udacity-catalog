################################################################################
''' Connect to a db, and perform CRUD operations '''
# Creates a database connection, and provides methods to
# modify the db tables. Read operations are currently handled in the calling
# code, directly on the instance that is returned from this class.
# Author: Paul Hoefgen
################################################################################

# import standard modules:
from sqlalchemy import create_engine
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

# import custom db models for this project:
from dbsetup import Base, Resorts, Users, Runs, Reviews

def connect():
    ''' Return a DB connection '''
    engine = create_engine('sqlite:///drtysnow/data/drtysnow.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    s = DBSession()
    return s

def create_user(db_session, fname, lname, favorite_resort_id,
                                                admin, email, user_id, picture):
    ''' Generate a new user row in the drtysnow database '''
    new_user = Users(first_name = fname,
                     last_name = lname,
                     favourite_resort_id = favorite_resort_id,
                     administrator = admin,
                     email_address = email,
                     user_id = user_id,
                     user_picture = picture)
    db_session.add(new_user)
    db_session.commit()
    return

def create_resort(db_session, name, location, summary, picture):
    ''' Generate a new resort row in the drtysnow database '''

    new_resort = Resorts(resort_name=name,
                         resort_location=location,
                         resort_summary=summary,
                         resort_image = picture)

    db_session.add(new_resort)
    db_session.commit()
    return

def create_run(db_session, run_name, resort_id, run_description):
    ''' Generate a new run row in the drtysnow database '''

    new_run = Runs(run_name = run_name,
                 resort_id = resort_id,
                 run_description = run_description)

    db_session.add(new_run)
    db_session.commit()
    return

def create_reviews(db_session, run_id, rating, user_id, top_hazard, mid_hazard,
                                                bot_hazard, comments, time):
    ''' Generate a new user row in the drtysnow database '''

    new_review = Reviews(run_id = run_id,
                         rating = rating,
                         user_id = user_id,
                         top_hazard = top_hazard,
                         mid_hazard = mid_hazard,
                         bot_hazard = bot_hazard,
                         comments = comments)

    db_session.add(new_review)
    db_session.commit()
    return

def delete(db_session, table, id):
    ''' Take the name of any table, and the pre-determined primary key, use
        the reference to delete a single row.'''

    delete_me = db_session.query(table_name).filter_by(id=row_id).first()
    db_session.delete(delete_me)
    db_session.commit()
    return

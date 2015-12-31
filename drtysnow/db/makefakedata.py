# this script populates the drtysnow databases with random test data.

import string
import random
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Base, Users, Resorts, Runs, Reviews

def fakename(maxlength):
    '''Build a fake name string '''
    length = random.randrange(2, maxlength + 2)
    name = "".join([random.choice(string.letters).lower()
                                                       for i in xrange(length)])
    name = name[0].upper() + name[1:]
    return name

def lorem(length):
    '''Build a fake block of text of set length '''
    lorem = ""
    for i in range(length):
        lorem = lorem + fakename(random.randrange(1,15)) + " "
    return lorem

''' Fake data to populate the database.'''
def make_resorts(s):
    name = fakename(15)
    location = fakename(12)
    summary = lorem(25)
    new_resort = Resorts(resort_name = name,
                         resort_location=location,
                         resort_summary=summary)
    s.add(new_resort)
    s.commit()
    return

def make_users(s):
    first_name = fakename(8) + "fname"
    last_name = fakename(15) + "lname"
    email = first_name + '.' + last_name + '@fakemail.com'
    favourite_resort_id = random.randrange(1,19)
    administrator = False;

    new_user = Users(first_name = first_name,
                     last_name = last_name,
                     email_address = email,
                     favourite_resort_id = favourite_resort_id,
                     administrator = administrator
                     )
    s.add(new_user)
    s.commit()
    return

def make_runs(s):
    run_name = fakename(4) + " " + fakename(15)
    resort_id = random.randrange(1,19)
    run_desc = lorem(50)

    new_run = Runs(run_name = run_name,
                    resort_id = resort_id,
                    run_description = run_desc)

    s.add(new_run)
    s.commit()

def make_reviews(s):
    run_id = random.randrange(1,19)
    rating = random.randrange(1,10)
    user_id = random.randrange(1,50)
    top_hazard = random.choice([True,False])
    mid_hazard = random.choice([True,False])
    bot_hazard = random.choice([True,False])
    comments = lorem(20)
    time = datetime.datetime.now()


    new_review = Reviews(run_id = run_id,
                         rating = rating,
                         user_id = user_id,
                         top_hazard = top_hazard,
                         mid_hazard = mid_hazard,
                         bot_hazard = bot_hazard,
                         comments = comments,
                         time = time)
    s.add(new_review)
    s.commit()


def main():

    engine = create_engine('sqlite:///drtysnow.db')
    Base.metadata.bind = engine
    DBsession = sessionmaker(bind = engine)
    s = DBsession()

    for i in range(50):
        make_resorts(s)
        make_users(s)
        make_runs(s)
        make_reviews(s)

    print "Added 50 rows to all tables."


if __name__ == '__main__':
    main()

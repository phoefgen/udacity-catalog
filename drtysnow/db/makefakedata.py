# this script populates the drtysnow databases with random test data.

import string
import random
import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Base, Users, Resorts, Runs, Reviews

def fakename(count):
    '''Build a fake name string '''
    names = ['Dominic Greear',
            'Olimpia Sturman',
            'Cristie Dewalt',
            'Corrina Mcgarrah',
            'Karina Span',
            'Karol Ramsier',
            'Luanna Balke',
            'Laci Wallick',
            'Vida Leggett',
            'Remona Alva',
            'Ferdinand Klosterman']
    return names[count]


def lorem(length):
    '''Build a fake block of text of set length '''

    f = open('lorem', 'r')
    words = list(f.read().split())
    lorem = u''
    for i in range(length):
        lorem = lorem + words[random.randrange(1,500)] + " "
    return lorem

''' Fake data to populate the database.'''
def make_resorts(s, count):
    '''
    Generate somewhat real looking fake ski resorts
    '''

    resort_names =['Apex Mountain',
                    'Big White',
                    'Blue Mountain',
                    'Calabogie Peaks',
                    'Camp Fortune',
                    'Canada Olympic Park',
                    'Castle Mountain',
                    'Cypress Mountain',
                    'Fernie Alpine',
                    'Grouse Mountain',
                    'Hemlock Resort']

    name = resort_names[count]

    resort_locations = ['British Columbia, CAN',
                        'Ontario, CAN',
                        'Quebec, CAN',
                        'Colorado, USA']
    resort_image = 'https://placeholdit.imgix.net/~text?txtsize=33&txt=Edit_Resort_Image&w=350&h=300'
    location = resort_locations[random.randint(0,3)]
    summary = lorem(25)
    new_resort = Resorts(resort_name = name,
                         resort_location=location,
                         resort_summary=summary,
                         resort_image=resort_image)
    s.add(new_resort)
    s.commit()
    return

def make_users(s, count):
    fullname = fakename(count)
    fullname = fullname.split()
    email = fullname[0] + '.' + fullname[1] + '@fakemail.com'
    favourite_resort_id = random.randrange(1,9)
    user_id = count + random.randrange(999,99999)
    administrator = False;

    new_user = Users(first_name = fullname[0],
                     last_name = fullname[1],
                     email_address = email,
                     favourite_resort_id = favourite_resort_id,
                     administrator = administrator,
                     user_id= user_id
                     )
    s.add(new_user)
    s.commit()
    return

def make_runs(s):
    for i in range(10):
        run_name = lorem(1) + " " + lorem(1)
        resort_id = random.randrange(0,9)
        run_desc = lorem(50)

        new_run = Runs(run_name = run_name,
                        resort_id = resort_id,
                        run_description = run_desc)

        s.add(new_run)
        s.commit()
    return

def make_reviews(s):

    for i in range(10):
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
    return


def main():

    engine = create_engine('sqlite:///drtysnow.db')
    Base.metadata.bind = engine
    DBsession = sessionmaker(bind = engine)
    s = DBsession()

    for i in range(10):
        make_resorts(s, i)
        make_users(s, i)
        make_runs(s)
        make_reviews(s)

    print "Added 10 rows to all tables."


if __name__ == '__main__':
    main()

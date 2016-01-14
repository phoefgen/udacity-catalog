################################################################################
''' Create and configure the database and tables '''
# Defines the arributes of the data model, and generates an empty database file
# Author: Paul Hoefgen
################################################################################

import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy import create_engine, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# This class Defines the DB table that stores records about the resorts.
class Resorts(Base):
    __tablename__ = 'resorts'

    id = Column(
        Integer,
        primary_key = True
        )

    resort_name = Column(
        String(100),
        nullable = False,
        unique = True
        )

    resort_location = Column(
        String(25),
        nullable = False
        )

    resort_image = Column(
        String(100),
        nullable = True
        )

    resort_summary = Column(
        String(100),
        nullable = False
    )

    runs = relationship("Runs", backref="runs")

# This class Defines the DB table that stores records about the Users.
class Users(Base):
    __tablename__ = 'users'

    id = Column(
        Integer,
        primary_key = True
    )

    user_id = Column(
        Integer,
        nullable = False
    )

    first_name = Column(
        String(100),
        nullable = False
    )

    last_name = Column(
        String(100),
        nullable = False
    )

    favourite_resort_id = Column(
        Integer,
        ForeignKey('resorts.id')
    )

    administrator = Column(
        Boolean
    )

    email_address = Column(
        String(100),
        nullable = False
    )

    user_picture =  Column(
        String(500),
    )

    resorts = relationship(Resorts)

# This class Defines the DB table that stores records about specifc Runs.
class Runs(Base):
    __tablename__ = 'runs'

    id = Column(
        Integer,
        primary_key = True
    )

    run_name = Column(
        String(100),
        nullable = False
    )

    resort_id = Column(
        Integer,
        ForeignKey('resorts.id')
    )

    run_description = Column(
        String(900),
        nullable = False
    )

    resorts = relationship(Resorts)



# This class Defines the DB table that stores all the run reviews.
class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(
        Integer,
        primary_key = True
    )

    run_id = Column(
        Integer,
        ForeignKey('runs.id')
    )

    rating = Column(
        Integer
    )

    user_id = Column(
        Integer,
        ForeignKey('users.id')
    )

    top_hazard = Column(
        Boolean
    )

    mid_hazard = Column(
        Boolean
    )

    bot_hazard = Column(
        Boolean
    )

    comments = Column(
        String(500)
    )

    time = Column(
        DateTime,
    )

    runs = relationship(Runs)
    users = relationship(Users)


engine = create_engine('sqlite:///drtysnow.db')
Base.metadata.create_all(engine)

import json
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, create_engine

database_path = os.environ.get('DATABASE_URL')
if not database_path:
    database_name = "capstone"
    database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
    binds a flask application and a SQLAlchemy service
    :param app: app
    :param database_path: database path
    :return:
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.create_all()


class Movie(db.Model):
    """
    Movie Database
    """
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        """

        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """

        :return:
        """
        db.session.commit()

    def delete(self):
        """

        :return:
        """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }


class Actor(db.Model):
    """

    """
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        """

        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """

        :return:
        """
        db.session.commit()

    def delete(self):
        """
        """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }

import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date

database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """
    Binds a flask application and a SQLAlchemy service
    :param app: app
    :param database_path: database path
    :return: Nothing
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
        Insert a new Movie record
        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Update movie record
        :return:
        """
        db.session.commit()

    def delete(self):
        """
        Delete movie record
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
    Actor database
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
        Insert actor record
        :return:
        """
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Update actor record
        :return:
        """
        db.session.commit()

    def delete(self):
        """
        Delete actor record
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

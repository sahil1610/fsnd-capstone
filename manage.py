from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from models import db, Actor, Movie

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def add_test_data():
    """
    Manager command to seed some test data
    :return:
    """
    Movie(title='Ludo', release_date='2020-07-11').insert()
    Movie(title='Challang',
          release_date='2020-07-11').insert()

    Actor(name='Amitabh Bachchan', age=78, gender='male').insert()
    Actor(name='Aamir Khan', age=50, gender='male').insert()


if __name__ == '__main__':
    manager.run()

import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor


def create_test_movie(data):
    """
    Create a test movie record
    :param data: {"title": "Movie_Title", "release_data": "2020-10-10"}
    :return: Created Movie instance
    """
    movie = Movie(**data)
    movie.insert()
    return movie


def create_test_actor(data):
    """
    Create a test actor record
    :param data: {"name": "Test Actor", "gender": "Male", "age": 55}
    :return: Created Actor instance
    """
    actor = Actor(**data)
    actor.insert()
    return actor


class MoviesTestCase(unittest.TestCase):
    """This class represents the Capstone Project test cases"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = os.getenv("DATABASE_URL")
        self.test_movie_data = {
            'title': 'Interstellar',
            'release_date': '2015-10-20'
        }
        self.patch_test_movie_data = {
            'title': 'Interstellar Updated',
        }
        self.test_actor_data = {
            'name': 'Shahrukh Khan',
            'age': 55,
            'gender': 'Male'
        }
        self.patch_test_actor_data = {
            'name': 'Shahrukh Khan Updated',
        }
        # Casting Assistant (can view movies and actors)
        casting_assistant_token = os.getenv("CASTING_ASSISTANT_TOKEN")
        # Casting Director (Casting Assistant role + can add, delete, patch
        # actors, can patch movies)
        casting_director_token = os.getenv("CASTING_DIRECTOR_TOKEN")
        # Executive Producer (Casting Director role + can add, delete, patch
        # actors and movies)
        executive_producer_token = os.getenv("EXECUTIVE_PRODUCER_TOKEN")
        setup_db(self.app, self.database_path)
        # Headers for different roles
        self.casting_assistant_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + casting_assistant_token,
        }
        self.casting_director_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + casting_director_token,
        }
        self.executive_producer_header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + executive_producer_token,
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test, all records are dropped from DB after each test"""
        with self.app.app_context():
            self.db.session.query(Movie).delete()
            self.db.session.query(Actor).delete()
            self.db.session.commit()

    def test_post_movie_executive_producer(self):
        response = self.client().post(
            f'/api/movie',
            data=json.dumps(
                self.test_movie_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], self.test_movie_data['title'])
        self.assertTrue(data['id'])

    def test_post_movie_when_movie_already_exists(self):
        create_test_movie(self.test_movie_data)
        response = self.client().post(
            f'/api/movie',
            data=json.dumps(
                self.test_movie_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            data['message'],
            f'Movie with name {self.test_movie_data["title"]} already exists.')

    def test_post_movie_when_blank_json_body_is_passed(self):
        response = self.client().post(f'/api/movie', data=json.dumps({}),
                                      content_type='application/json',
                                      headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_post_movie_casting_director(self):
        response = self.client().post(
            f'/api/movie',
            data=json.dumps(
                self.test_movie_data),
            content_type='application/json',
            headers=self.casting_director_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_patch_movie_executive_producer(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().patch(
            f'/api/movie/{movie.id}',
            data=json.dumps(
                self.patch_test_movie_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(
            data['movie']['title'],
            self.patch_test_movie_data['title'])

    def test_patch_movie_casting_director(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().patch(
            f'/api/movie/{movie.id}',
            data=json.dumps(
                self.patch_test_movie_data),
            content_type='application/json',
            headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(
            data['movie']['title'],
            self.patch_test_movie_data['title'])

    def test_patch_movie_casting_assistant(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().patch(
            f'/api/movie/{movie.id}',
            data=json.dumps(
                self.patch_test_movie_data),
            content_type='application/json',
            headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_patch_movie_when_id_is_invalid(self):
        movie_id = 0
        response = self.client().patch(
            f'/api/movie/{movie_id}',
            data=json.dumps(
                self.test_movie_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            data['message'],
            f'Movie with id: {movie_id} does not exist')

    def test_patch_movie_when_blank_json_body_is_passed(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().patch(
            f'/api/movie/{movie.id}',
            data=json.dumps(
                {}),
            content_type='application/json',
            headers=self.casting_director_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_delete_movie_executive_producer(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().delete(f'/api/movie/{movie.id}',
                                        headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['deleted'], movie.id)

    def test_delete_movie_casting_director(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().delete(f'/api/movie/{movie.id}',
                                        headers=self.casting_director_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_movie_casting_assistant(self):
        movie = create_test_movie(self.test_movie_data)
        response = self.client().delete(f'/api/movie/{movie.id}',
                                        headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_movie_when_id_is_invalid(self):
        movie_id = 0
        response = self.client().delete(f'/api/movie/{movie_id}',
                                        headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            data['message'],
            f'Movie with id: {movie_id} does not exist')

    def test_get_movie_casting_assistant(self):
        create_test_movie(self.test_movie_data)
        response = self.client().get(f'/api/movie',
                                     headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['movies'], list)
        self.assertEqual(len(data['movies']), len(Movie.query.all()))

    def test_get_movie_casting_director(self):
        create_test_movie(self.test_movie_data)
        response = self.client().get(f'/api/movie',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['movies'], list)
        self.assertEqual(len(data['movies']), len(Movie.query.all()))

    def test_get_movie_executive_producer(self):
        create_test_movie(self.test_movie_data)
        response = self.client().get(f'/api/movie',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['movies'], list)
        self.assertEqual(len(data['movies']), len(Movie.query.all()))

    def test_get_movie_when_no_movie_exists(self):
        response = self.client().get(f'/api/movie',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(
            data['message'],
            'No movie present, please add movies using the API')

    def test_get_actor_casting_assistant(self):
        create_test_actor(self.test_actor_data)
        response = self.client().get(f'/api/actor',
                                     headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['actors'], list)
        self.assertEqual(len(data['actors']), len(Actor.query.all()))

    def test_get_actor_casting_director(self):
        create_test_actor(self.test_actor_data)
        response = self.client().get(f'/api/actor',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['actors'], list)
        self.assertEqual(len(data['actors']), len(Actor.query.all()))

    def test_get_actor_executive_producer(self):
        create_test_actor(self.test_actor_data)
        response = self.client().get(f'/api/actor',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['actors'], list)
        self.assertEqual(len(data['actors']), len(Actor.query.all()))

    def test_get_actor_when_no_actor_exists(self):
        response = self.client().get(f'/api/actor',
                                     headers=self.casting_director_header)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(
            data['message'],
            'No actor present, please add movies using the API')

    def test_post_actor_casting_director(self):
        response = self.client().post(
            f'/api/actor',
            data=json.dumps(
                self.test_actor_data),
            content_type='application/json',
            headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], self.test_actor_data['name'])
        self.assertEqual(data['age'], self.test_actor_data['age'])
        self.assertEqual(data['gender'], self.test_actor_data['gender'])
        self.assertTrue(data['id'])

    def test_post_actor_executive_producer(self):
        response = self.client().post(
            f'/api/actor',
            data=json.dumps(
                self.test_actor_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], self.test_actor_data['name'])
        self.assertEqual(data['age'], self.test_actor_data['age'])
        self.assertEqual(data['gender'], self.test_actor_data['gender'])
        self.assertTrue(data['id'])

    def test_post_actor_when_actor_already_exists(self):
        create_test_actor(self.test_actor_data)
        response = self.client().post(
            f'/api/actor',
            data=json.dumps(
                self.test_actor_data),
            content_type='application/json',
            headers=self.casting_director_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            data['message'],
            f'Actor with name {self.test_actor_data["name"]} already exists.')

    def test_post_actor_when_blank_json_body_is_passed(self):
        response = self.client().post(f'/api/actor', data=json.dumps({}),
                                      content_type='application/json',
                                      headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_post_movie_casting_assistant(self):
        response = self.client().post(
            f'/api/actor',
            data=json.dumps(
                self.test_actor_data),
            content_type='application/json',
            headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_patch_actor_executive_producer(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().patch(
            f'/api/actor/{actor.id}',
            data=json.dumps(
                self.patch_test_actor_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(
            data['updated_actor']['name'],
            self.patch_test_actor_data['name'])

    def test_patch_actor_casting_director(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().patch(
            f'/api/actor/{actor.id}',
            data=json.dumps(
                self.patch_test_actor_data),
            content_type='application/json',
            headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(
            data['updated_actor']['name'],
            self.patch_test_actor_data['name'])

    def test_patch_actor_casting_assistant(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().patch(
            f'/api/actor/{actor.id}',
            data=json.dumps(
                self.patch_test_actor_data),
            content_type='application/json',
            headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_patch_actor_when_id_is_invalid(self):
        actor_id = 0
        response = self.client().patch(
            f'/api/actor/{actor_id}',
            data=json.dumps(
                self.patch_test_actor_data),
            content_type='application/json',
            headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            data['message'],
            f'Actor with id: {actor_id} does not exist')

    def test_patch_actor_when_blank_json_body_is_passed(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().patch(
            f'/api/actor/{actor.id}',
            data=json.dumps(
                {}),
            content_type='application/json',
            headers=self.casting_director_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_delete_actor_executive_producer(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().delete(f'/api/actor/{actor.id}',
                                        headers=self.executive_producer_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['deleted'], actor.id)

    def test_delete_actor_casting_director(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().delete(f'/api/actor/{actor.id}',
                                        headers=self.casting_director_header)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['deleted'], actor.id)

    def test_delete_actor_casting_assistant(self):
        actor = create_test_actor(self.test_actor_data)
        response = self.client().delete(f'/api/actor/{actor.id}',
                                        headers=self.casting_assistant_header)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_actor_when_id_is_invalid(self):
        actor_id = 0
        response = self.client().delete(f'/api/actor/{actor_id}',
                                        headers=self.executive_producer_header)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            data['message'],
            f'Actor with id: {actor_id} does not exist')


# # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

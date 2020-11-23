#!/usr/bin/env python3
import os

from auth.auth import AuthError, requires_auth
from flask import Flask, request, abort, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Movie, Actor

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    @app.route('/')
    def home_page():
        AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
        AUTH0_CALLBACK_URL = os.getenv("CALLBACK_URL")
        API_AUDIENCE = os.getenv("API_AUDIENCE")
        CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
        url = (
            f'https://{AUTH0_DOMAIN}/authorize?audience={API_AUDIENCE}&response_type=token&client_id={CLIENT_ID}'
            f'&redirect_uri={AUTH0_CALLBACK_URL}'
        )
        return render_template('pages/home.html', url=url)

        # return f'If the JWT tokens in the downloaded project folder expired please follow the README.txt for ' \
        #        f'instructions and request new JWT tokens at this URL: {url}'

    @app.route('/api/movie', methods=['GET'])
    @requires_auth('get:movie')
    def get_movies(payload):
        movies = Movie.query.all()
        if len(movies) == 0:
            abort(404, 'No movie present, please add movies using the API')

        try:
            movie_list_json = [movie.serialize() for movie in movies]
            return jsonify({
                'success': True,
                'movies': movie_list_json
            })
        except Exception as e:
            abort(422, str(e))

    @app.route('/api/actor', methods=['GET'])
    # @requires_auth('get:actor')
    def get_actors():
        actors = Actor.query.all()
        if len(actors) == 0:
            abort(404, 'No actor present, please add movies using the API')

        try:
            actor_list_json = [actor.serialize() for actor in actors]
            return jsonify({
                'success': True,
                'actors': actor_list_json
            })
        except Exception as e:
            abort(422, str(e))

    @app.route('/api/movie', methods=['POST'])
    @requires_auth('post:movie')
    def add_movie(payload):
        body = request.get_json()
        if not body:
            # posting an empty json should return a 400 error.
            abort(400, 'JSON passed is empty')
        if 'title' not in body.keys() or 'release_date' not in body.keys():
            abort(400, 'Invalid JSON, "title" or "release_date" key is not present')

        if Movie.query.filter_by(title=body['title']).first():
            abort(409, 'Movie with name ' + body['title'] + ' already exists.')
        try:
            movie = Movie(title=body['title'], release_date=body['release_date'])
            movie.insert()
            return jsonify(movie.serialize())
        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    @app.route('/api/movie/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(payload, movie_id):

        movie = Movie.query.filter_by(id=movie_id).one_or_none()
        if movie is None:
            abort(404, f'Movie with id: {movie_id} does not exist')
        try:
            movie.delete()
            return jsonify({
                'success': True,
                'deleted': str(movie_id)
            })
        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    @app.route('/api/movie/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def update_movie(payload, movie_id):
        movie = Movie.query.filter_by(id=movie_id).one_or_none()
        if movie is None:
            abort(404, f'Movie with id: {movie_id} does not exist')

        body = request.get_json()
        if not body:
            # posting an empty json should return a 400 error.
            abort(400, 'JSON passed is empty')
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        if not title and not release_date:
            abort(400, 'Both title and release_date are "None"')
        try:
            movie.title = title or movie.title
            movie.release_date = release_date or movie.release_date
            movie.update()
            return jsonify({
                'success': True,
                'movie': movie.serialize()
            })

        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    @app.route('/api/actor', methods=['POST'])
    @requires_auth('post:actor')
    def add_actor(payload):
        body = request.get_json()
        if not body:
            # posting an empty json should return a 400 error.
            abort(400, 'JSON passed is empty')
        if 'name' not in body.keys() or 'age' not in body.keys() or 'gender' not in body.keys():
            abort(400, 'Invalid JSON, "name" or "age" or "gender" key is not present')
        data = {
            'name': body['name'],
            'age': body['age'],
            'gender': body['gender'],
        }
        if Actor.query.filter_by(name=body['name']).first():
            abort(409, 'Actor with name ' + body['name'] + ' already exists.')
        try:
            actor = Actor(name=body['name'], age=body['age'], gender=body['gender'])
            actor.insert()
            return jsonify(actor.serialize())
        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    @app.route('/api/actor/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(payload, actor_id):

        movie = Actor.query.filter_by(id=actor_id).one_or_none()
        if movie is None:
            abort(404, f'Actor with id: {actor_id} does not exist')
        try:
            movie.delete()
            return jsonify({
                'success': True,
                'deleted': str(actor_id)
            })
        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    @app.route('/api/actor/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def update_actor(payload, actor_id):
        actor = Actor.query.filter_by(id=actor_id).one_or_none()
        if actor is None:
            abort(404, f'Actor with id: {actor_id} does not exist')

        body = request.get_json()
        if not body:
            # posting an empty json should return a 400 error.
            abort(400, 'JSON passed is empty')
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        if not name and not age and not gender:
            abort(400, 'Name, Age and Gender are "None"')
        try:
            actor.name = name or actor.name
            actor.age = age or actor.age
            actor.gender = age or actor.gender
            actor.update()
            return jsonify({
                'success': True,
                'updated_actor': actor.serialize()
            })

        except Exception as e:
            db.session.rollback()
            abort(422, str(e))
        finally:
            db.session.close()

    # Error handling

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': getattr(error, 'description', 'Bad Request')
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            "message": getattr(error, 'description', 'Resource Not Found')
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            "message": 'Method not allowed'
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'success': False,
            'error': 409,
            'message': getattr(error, 'description', 'Resource Already Exists')
        }), 409

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": getattr(error, 'description', 'unprocessable')
        }), 422

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

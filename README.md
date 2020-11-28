Udacity Full Stack Developer Nanodegree Capstone Project
-----

### Motivation
This project is the Capstone Project for the Udacity Full Stack Developer Nanodegree. Here we have created backend and a basic frontend to demonstrate what we have learned in the course of this Nanodegree, like creating a rest API, accessing endpoints based on different roles (RBAC) using JWT authentication, writing unit tests for REST API endpoints and error handling.

### Overview
This project is for a Casting Agency which is having Movies and Actors. As of now, both Movies and Actors are independent identity and have no relationship among themselves. 

Different users can access, add and modify Movie and Actor details based on their permission set. There are three different roles and all these three roles have different set of permissions as defined below:

* **Casting Assistant** - 
 -  Can view actors and movies
* **Casting Director** - 
 - All permissions a Casting Assistant has and..
 - Add or delete an actor from the database
 - Modify actors or movies
* **Executive Producer**
 - All permissions a Casting Director has and..
 - Add or delete a movie from the database

### Live App
The app is deployed on Heroku and can be accessed at [https://udacity-capstone-sahil.herokuapp.com/](https://udacity-capstone-sahil.herokuapp.com/)

### Account Details
* **Casting Assistant** - castingassistant@sahilfsnd.com
* **Casting Director** - castingdirector@sahilfsnd.com
* **Executive Producer** - executiveproducer@sahilfsnd.com

The password for all these accounts is `Welcome123`. Test JWT tokens are present in Setup.sh which are valid till 29 Nov 2020, 5:17 PM IST.

### Tech Stack

Our tech stack will include:

* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**,  **Javascript** with for our website's basic frontend
* **Heroku**: Our Deployment Platform [https://www.heroku.com/](https://www.heroku.com/)

Make sure all of the above are installed.

### Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

  ```
  $ cd ~
  $ sudo pip3 install Flask
  ```

To start and run the local development server,
1. **Clone the Repository**
    ```bash
    git clone -b master https://github.com/sahil1610/fsnd-capstone.git
    ```

2. **Set up the virtual environment**:
    ```bash
    virtualenv env
    source env/Scripts/activate # for windows
    source env/bin/activate # for MacOs
    ```

3. **Install Project Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Create Local Database**:
    Create a local database and export the database URI as an environment variable with the key `DATABASE_PATH`.
    ```bash
    createdb <db_name>
    ```

5. **Export Environment Variables**
    Refer to the `setup.sh` file, update the required variable accordingly and export the environment variables for the project:
    ```bash
    source setup.sh
    ```

6. **Run Database Migrations and Add Test Data**:
    ```bash
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py add_test_data
    ```

7. **Run the Flask Application locally**:
    ```bash
    export FLASK_APP=myapp
    export FLASK_ENV=development
    flask run
    ```
8. Navigate to Home page [http://localhost:5000](http://localhost:5000), which is having a login link clicking on which open the Auth0 Login page.

### Application Homepage
![Home page](https://github.com/sahil1610/fsnd-capstone/blob/main/HomePage.png)

The homepage can be used to login and generate JWT token. for a specific user and also to refresh the token if token being used has expired. There is also a button to logout.

## Endpoints
### Getting Started
- Base URL: currently the server runs locally on `http://127.0.0.1:5000/` and is also deployed on Heroku at [https://udacity-capstone-sahil.herokuapp.com/](https://udacity-capstone-sahil.herokuapp.com/).
- Authentication: Is configured for three different roles i.e. Casting Assistant, Casting Director, and Executive Producer. 

### Error Handling
Flask's `@app.errorhandler` decorators are implemented for:
- 400: Bad Request
- 404: Resource not found
- 405: Method Not Allowed
- 409: Conflict
- 401: Token Expired
- 403: Permission Not Found

Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 404,
    "message": "<Custom error message>"
}
```

### Movies
#### GET /api/movie
- **General**: Returns the list of all movies
- **Authorization**: All three roles i.e. Casting Assistant, Casting Director and Executive Producer are authorized to use this end point
- **Sample**: `curl  --request GET 'localhost:5000/api/movie' \
--header 'Authorization: Bearer <JWT_TOKEN>'`
    ```{
       "movies":[
          {
             "id": 1,
             "title":"Interstellar",
             "release_date":"2015-10-10"
          },
          {
             "id": 2,
             "title":"Avengers End Game",
             "release_date":"2019-05-10"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 is no movie is present in the Database

#### POST /api/movie/
- **General**: To add a new movie to the database
- **Authorization**: Only Executive Producer is authorized to use this end point
- **Sample**: `curl  --request POST 'localhost:5000/api/movie' \
--header 'Authorization: Bearer <JWT_TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "title": "Movie Title",
    "release_date":"2020-10-10"
}'`
    ```{
       "movie":[
          {
             "id": 1,
             "title":"Movie Title",
             "release_date":"2020-10-10"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 400 if JSON input passed is empty or if title or release_date key is missing
    - Returns 409 if Movie with same name is already present

#### PATCH /api/movie/<movie_id>
- **General**: To update movie title and release with given id
- **Request Arguments**: <movie_id> which is the ID of the movie to be edited 
- **Authorization**: Casting Director and Executive Producer are authorized to use this end point
- **Sample**: `curl  --request PATCH 'localhost:5000/api/movie/1' \
--header 'Authorization: Bearer <JWT_TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "title": "Updated Title",
    "release_date":"2020-10-10"
}'`
    ```{
       "movie":[
          {
             "id": 1,
             "title":"Updated Title",
             "release_date":"2020-10-10"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 if movie with ID is not present in the Database
    - Returns 400 if JSON input passed is empty or if keys are None
    
#### DELETE /api/movie/<movie_id>
- **General**: To delete a movie with given id
- **Request Arguments**: <movie_id> which is the ID of the movie to be deleted 
- **Authorization**: Only Executive Producer are authorized to use this end point
- **Sample**: `curl  --request DELETE 'localhost:5000/api/movie/1' \
--header 'Authorization: Bearer <JWT_TOKEN>'`
    ```{
       "deleted": <movie_id>
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 if movie with ID is not present in the Database
    
### Actors
#### GET /api/actor
- **General**: Returns the list of all actors
- **Authorization**: All three roles i.e. Casting Assistant, Casting Director and Executive Producer are authorized to use this end point
- **Sample**: `curl  --request GET 'localhost:5000/api/actor' \
--header 'Authorization: Bearer <JWT_TOKEN>'`
    ```{
       "actors":[
          {
             "id": 1,
             "name":"Amitabh Bachchan",
             "age":75",
             "gender": "Male"
          },
          {
             "id": 2,
             "name":"Salman Khan",
             "age":55",
             "gender": "Male"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 is no actor is present in the Database

#### POST /api/actor/
- **General**: To add a new actor to the database
- **Authorization**: Only Executive Producer is authorized to use this end point
- **Sample**: `curl  --request POST 'localhost:5000/api/actor' \
--header 'Authorization: Bearer <JWT_TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
     "name":"Salman Khan",
     "age":55",
     "gender": "Male"
  }'`
    ```{
       "actor":[
          {
             "id": 1,
             "name":"Salman Khan",
             "age":55",
             "gender": "Male"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 400 if JSON input passed is empty or if name or age or gender key is missing
    - Returns 409 if Actor with same name is already present

#### PATCH /api/actor/<actor_id>
- **General**: To edit actors name, age and gender with the give id
- **Request Arguments**: <actor_id> which is the ID of the actor to be edited 
- **Authorization**: Casting Director and Executive Producer are authorized to use this end point
- **Sample**: `curl  --request PATCH 'localhost:5000/api/actor/1' \
--header 'Authorization: Bearer <JWT_TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Updated Actor",
    "age": "50",
    "gender": "Female"
}'`
    ```{
       "actor":[
          {
             "id": 1,
             "name": "Updated Actor",
             "age": "50",
             "gender": "Female"
          }
       ],
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 if actor with ID is not present in the Database
    - Returns 400 if JSON input passed is empty or if keys are None
    
#### DELETE /api/actor/<actor_id>
- **General**: To delete actor with the give id
- **Request Arguments**: <actor_id> which is the ID of the actor to be deleted 
- **Authorization**: Casting Director and Executive Producer are authorized to use this end point
- **Sample**: `curl  --request DELETE 'localhost:5000/api/actor/1' \
--header 'Authorization: Bearer <JWT_TOKEN>'`
    ```{
       "deleted": <actor_id>
       "success":true
    }
    ```
- **Errors**:
    - Returns 404 if movie with ID is not present in the Database
    
  

## Testing
In order to run the tests, run the following in shell/bash, provided Postgres is installed.
```bash
dropdb capstone_test
createdb capstone_test
source setup.sh
python test_capstone.py
```

import json
import unittest
from unittest import mock

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.sample_question_body = {
            'question': 'New Sample Question',
            'answer': 'sample answer',
            'difficulty': 1,
            'category': 1
        }

        self.sample_question_body_invalid = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
        # create question before every test which can be used for testing purpose.
        # We would be clearning up this question after every tests
        self.mock_question = create_question()
        self.mock_question_id = self.mock_question.id

    def tearDown(self):
        """Executed after reach test"""
        # checking for existence of question before deletion
        if Question.query.get(self.mock_question_id):
            self.mock_question.delete()
        pass

    def test_get_all_categories(self):
        """
        Test /api/v1/categories end point to return dictionary of all categories
        """
        res = self.client().get('/api/v1/categories')
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['categories'], dict)

    @mock.patch('flask_sqlalchemy._QueryProperty.__get__')
    def test_get_all_categories_returns_404_if_no_category_is_present(self, query_mock):
        """
        Test /api/v1/categories returns 404 if no category is present
        """
        query_mock.return_value.order_by.return_value.all.return_value = []
        res = self.client().get('/api/v1/categories')
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No category is present')

    def test_get_all_questions(self):
        """
        Test /api/v1/questions returns all questions in a paginated fashion
        """
        res = self.client().get('/api/v1/questions?page=1')
        data = json.loads(res.data)
        expected_questions = Question.query.all()
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['categories'], dict)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(data['total_questions'], len(expected_questions))

    @mock.patch('flask_sqlalchemy._QueryProperty.__get__')
    def test_get_all_questions_returns_404_if_no_question_is_present(self, query_mock):
        """
        Test /api/v1/questions returns 404 if not question is present
        """
        query_mock.return_value.order_by.return_value.all.return_value = []
        res = self.client().get('/api/v1/questions?page=1')
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No question is present, please add a question and then try')

    def test_get_all_questions_returns_404_page_number_is_out_of_range(self):
        """
        Test /api/v1/questions returns 404 if the page number passed is out of range
        """
        res = self.client().get('/api/v1/questions?page=100000000')
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No question is present for the page number 100000000')

    def test_delete_question_success(self):
        """
        Test /api/v1/questions/<question_id> deletes question successfully
        """
        mock_question_id = self.mock_question_id
        res = self.client().delete(f'/api/v1/questions/{mock_question_id}')
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['question_id'], mock_question_id)

    def test_delete_question_when_question_not_found(self):
        """
         Test /api/v1/questions/<question_id> returns 404 if passed question id is not found
        """
        res = self.client().delete('/api/v1/questions/100000000')
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Question with id=100000000 is not present')

    @mock.patch.object(Question, 'delete')
    def test_delete_question_in_case_of_server_error(self, mock_delete):
        """
         Test /api/v1/questions/<question_id> returns 500 in case of interval server error while deleting question
        """
        mock_delete.side_effect = Exception('Internal Server Error!')
        mock_question_id = self.mock_question_id
        res = self.client().delete(f'/api/v1/questions/{mock_question_id}')
        data = json.loads(res.data)
        # status code should be 500
        self.assertEqual(res.status_code, 500)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unable to delete the question. Error - Internal Server Error!')

    def test_get_all_questions_by_category_when_category_exists(self):
        """
         Test /api/v1/categories/<category_id>/questions to return questions for a particular category
        """
        category_id = 1
        res = self.client().get(f'/api/v1/categories/{category_id}/questions')
        data = json.loads(res.data)
        expected_questions = Question.query.filter_by(category=category_id).all()
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'], category_id)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(data['total_questions'], len(expected_questions))

    def test_get_all_questions_by_category_when_category_doesnot_exists(self):
        """
        Test /api/v1/categories/<category_id>/questions to return 404 when category id passed doesn't exist
        """
        category_id = Category.query.order_by(desc(Category.id)).first().id + 1
        res = self.client().get(f'/api/v1/categories/{category_id}/questions')
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], f'Category with id {category_id} doesn\'t exist')

    def test_get_all_questions_by_category_when_no_question_for_given_category(self):
        """
        Test /api/v1/categories/<category_id>/questions to return 404 when no question exist for a particular category
        """
        category_id = Category.query.order_by(func.random()).first().id
        with mock.patch('flask_sqlalchemy._QueryProperty.__get__') as query_mock:
            query_mock.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
            res = self.client().get(f'/api/v1/categories/{category_id}/questions')
            data = json.loads(res.data)
            # status code should be 404
            self.assertEqual(res.status_code, 404)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], f'No question found for the category id {category_id}')

    def test_create_new_question_success(self):
        """
        Test /api/v1/questions successfully creates a question
        """
        res = self.client().post('/api/v1/questions', json=self.sample_question_body)
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('created_question', data)
        self.assertIn('id', data)
        created_question_id = data['id']
        question = Question.query.get(created_question_id)
        self.assertIsNotNone(question)
        self.assertEqual(self.sample_question_body['question'], question.question)
        self.assertEqual(self.sample_question_body['answer'], question.answer)
        self.assertEqual(self.sample_question_body['category'], question.category)
        self.assertEqual(self.sample_question_body['difficulty'], question.difficulty)

    def test_create_new_question_with_empty_json(self):
        """
        Test /api/v1/questions returns 400 when empty json is passed in post request
        """
        res = self.client().post('/api/v1/questions', json={})
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_create_new_question_with_missing_fields_value(self):
        """
        Test /api/v1/questions returns 400 when a key is missing in the input json
        """
        res = self.client().post('/api/v1/questions', json=self.sample_question_body_invalid)
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Either of the question, answer, difficulty or category is not passed')

    def test_search_question_success(self):
        """
        Test /api/v1/questions/search successfully searches a question
        """
        mock_question_id = self.mock_question_id
        search_term = Question.query.get(mock_question_id).question
        res = self.client().post('/api/v1/questions/search', json={
            'searchTerm': search_term
        })
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        self.assertIsInstance(data['total_questions'], int)
        self.assertEqual(data['total_questions'], 1)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)

    def test_search_question_invalid_search_term(self):
        """
        Test /api/v1/questions/search returns 404 when the search term is invalid
        """
        search_term = 'xxxxxxxblahxxxxxx'
        res = self.client().post('/api/v1/questions/search', json={
            'searchTerm': search_term
        })
        data = json.loads(res.data)
        # status code should be 404
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], f'No question found with search term "{search_term}"')

    def test_search_question_empty_search_term(self):
        """
        Test /api/v1/questions/search when search term passed is empty
        """
        res = self.client().post('/api/v1/questions/search', json={
            'searchTerm': ''
        })
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Search term is empty')

    def test_search_question_empty_json(self):
        """
        Test /api/v1/questions/search when search term passed is empty
        """
        res = self.client().post('/api/v1/questions/search', json={})
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_play_quiz_empty_json(self):
        """
        Test /api/v1/quizzes returns 400 if empty json is passed
        """
        res = self.client().post('/api/v1/quizzes', json={})
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'JSON passed is empty')

    def test_play_quiz_success(self):
        """
        Test /api/v1/quizzes successfully returns question
        """
        category_id = 1
        question_list = Question.query.filter_by(category=category_id).limit(1).all()
        previous_questions = [question.id for question in question_list]
        res = self.client().post('/api/v1/quizzes',
                                 json={'previous_questions': previous_questions,
                                       'quiz_category': {'id': category_id}})
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('question', data)
        self.assertIsInstance(data['question'], dict)
        self.assertIsNotNone(data['question'])

    def test_play_quiz_all_category(self):
        """
        Test play quiz when ALL has been selected as the category
        :return:
        """
        category_id = 0
        question_list = Question.query.limit(1).all()
        previous_questions = [question.id for question in question_list]
        res = self.client().post('/api/v1/quizzes',
                                 json={'previous_questions': previous_questions,
                                       'quiz_category': {'id': category_id}})
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('question', data)
        self.assertIsInstance(data['question'], dict)
        self.assertIsNotNone(data['question'])

    def test_play_quiz_missing_key(self):
        """
        Test play quiz when the key previous question is missing
        """
        category_id = 1
        res = self.client().post('/api/v1/quizzes',
                                 json={'quiz_category': {'id': category_id}})
        data = json.loads(res.data)
        # status code should be 400
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],
                         'Invalid input JSON, either quiz_category or previous_questions key is missing')

    def test_play_quiz_all_questions_played_out(self):
        """
        Test the case when all questions for a particular category have been played out
        """
        category_id = 1
        question_list = Question.query.filter_by(category=category_id).all()
        previous_questions = [question.id for question in question_list]
        res = self.client().post('/api/v1/quizzes',
                                 json={'previous_questions': previous_questions,
                                       'quiz_category': {'id': category_id}})
        data = json.loads(res.data)
        # status code should be 200
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'All questions are played out')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

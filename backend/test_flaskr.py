import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions_with_results(self):
        res = self.client().post('/search', json={'searchTerm':'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # two questions will be found: id_5 and id_6
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['questions'][0]['id'], 5)
        self.assertEqual(data['questions'][1]['id'], 6)

    def test_search_questions_without_result(self):
        res = self.client().post('/search', json={'searchTerm':'blahblah'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)

    def test_create_question(self):
        test_question = {
            'question':'What is the capital of Austria?',
            'answer':'Vienna',
            'category':'3',
            'difficulty':1
        }

        # get total number of questions BEFORE creating new question
        total_questions_1 = len(Question.query.all())

        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        # get total number of questions AFTER creating new question
        total_questions_2 = len(Question.query.all())

        createdQuestion = Question.query.filter_by(id=data['created']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(total_questions_2 - total_questions_1 == 1)
        self.assertEqual(createdQuestion.question, 'What is the capital of Austria?')

    def test_failed_create_question(self):
        test_question = {
            'a':'abc',
            'b':'def'
        }
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_delete_question(self):
        # add a new question to delete
        test_question = {
            'question':'What is the capital of Austria?',
            'answer':'Vienna',
            'category':'3',
            'difficulty':1
        }
        testQuestion = Question(question=test_question['question'],
        answer=test_question['answer'],
        category=test_question['category'],
        difficulty=test_question['difficulty'])
        testQuestion.insert()

        tgt_id = testQuestion.id
        # get total number of question BEFORE deleteing new question
        total_questions_1 = len(Question.query.all())

        res = self.client().delete('/questions/{}'.format(tgt_id))
        data = json.loads(res.data)
        # get total number of questions AFTER deleteing new question
        total_questions_2 = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], tgt_id)
        self.assertTrue(total_questions_1 - total_questions_2 == 1)

    def test_play_quiz(self):
        test_data = {
            'previous_questions':[],
            'quiz_category':{
                'id':1,
                'type':'Science'
            }
        }

        res = self.client().post('/quizzes', json=test_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_failed_play_quiz(self):
        test_data = {
            'previous_questions':[],
            'quiz_category':{
                'type':'Art'
            }
        }

        res = self.client().post('quizzes', json=test_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


        
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
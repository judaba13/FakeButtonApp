import json
import copy
import unittest
from flask import Flask
from flask.ext.pymongo import PyMongo
from handlers.user import user
from handlers.transfers import transfer
from db_utils.db_utils import mongo

MONGO_URL = "mongodb://localhost:27017/testfakebutton"
test_application = Flask(__name__)
#register all of the handlers with this app
test_application.register_blueprint(user)
test_application.register_blueprint(transfer)
test_application.config['MONGO_URI'] = MONGO_URL
test_application.config['MONGO_AUTO_START_REQUEST'] = False
test_application.config['TESTING'] = True
test_application.config['DEBUG'] = True
mongo.init_app(test_application)
test_app = test_application.test_client()

def response_success(response, code=None):
    if code is None:
        assert 200 <= response.status_code < 300, 'Received %d response: %s' % (response.status_code, response.data)
    else:
        assert code == response.status_code, 'Received %d response: %s' % (response.status_code, response.data)

def response_error(response, code=None):
    if code is None:
        assert 400 <= response.status_code < 500, 'Received %d response: %s' % (response.status_code, response.data)
    else:
        assert code == response.status_code, 'Received %d response: %s' % (response.status_code, response.data)

def compare_req_resp(req_obj, resp_obj):
    for k,v in req_obj.iteritems():
        assert k in resp_obj.keys(), 'Key %r not in response (keys are %r)' % (k, resp_obj.keys())
        assert resp_obj[k] == v, 'Value for key %r should be %r but is %r' % (k, v, resp_obj[k])


class FakeButtonAPITest(unittest.TestCase):

    def init_mongo(self, app):
      """
      A function that initializes the counter db to keep track of users
      """
      with app.app_context():
          if not mongo.db.counters.find_one({"_id": 'userid'}):
              mongo.db.counters.insert({'_id': 'userid',
                                        'seq': 0})
          else:
              mongo.db.counters.remove({'_id':'userid'})
              mongo.db.counters.insert({'_id': 'userid',
                                        'seq': 0})
          if not mongo.db.counters.find_one({"_id": 'transferid'}):
              mongo.db.counters.insert({'_id': 'transferid',
                                        'seq': 0})
          else:
              mongo.db.counters.remove({'_id':'transferid'})
              mongo.db.counters.insert({'_id': 'transferid',
                                        'seq': 0})

    def setUp(self):
        self.user_1 = {
                        'email': '1@b.com',
                        'firstName': 'justin',
                        'lastName': 'bard'
                      }

        self.user_2 = {
                        'email': '2@b.com',
                        'firstName': 'bob',
                        'lastName': 'smith'
                      }

        self.xfer_1 = {
                        "amount": 100,
                        "user_id": 1
                      }

        self.xfer_2 = {
                        "amount": -50,
                        "user_id": 2
                      }
        #check if there are no user counters in the db, and init if not
        self.init_mongo(test_application)
        self.app = test_app
        with test_application.app_context():
            # delete users from db
            mongo.db.users.delete_one({"_id": 1})
            mongo.db.users.delete_one({"_id": 2})
            mongo.db.transfers.delete_one({"_id": 1})
            mongo.db.transfers.delete_one({"_id": 2})

        # create user 1
        resp = self.app.post('/user', data=json.dumps(self.user_1),content_type='application/json')
        response_success(resp)
        self.user_1_obj = json.loads(resp.data)
        compare_req_resp(self.user_1, self.user_1_obj)

        # create user 2
        resp = self.app.post('/user', data=json.dumps(self.user_2),content_type='application/json')
        response_success(resp)
        self.user_2_obj = json.loads(resp.data)
        compare_req_resp(self.user_2, self.user_2_obj)

    def tearDown(self):
        # delete user 1
        resp = self.app.delete('/user/%s/' % self.user_1_obj['_id'])
        with test_application.app_context():
            mongo.db.users.delete_one({"_id": 1})
            mongo.db.transfers.delete_one({"_id": 1})
        resp = self.app.get('/user/%s/' % self.user_1_obj['_id'])
        response_error(resp, code=404)

        # delete user 2
        resp = self.app.delete('/user/%s/' % self.user_2_obj['_id'])
        with test_application.app_context():
            mongo.db.users.delete_one({"_id": 2})
            mongo.db.transfers.delete_one({"_id": 2})
        resp = self.app.get('/user/%s/' % self.user_2_obj['_id'])
        response_error(resp, code=404)

    def test_get_all_users(self):
        resp = self.app.get('/user')
        objs = json.loads(resp.data)
        self.assertEqual(len(objs), 2)

    def test_get_one_user(self):
        resp = self.app.get('/user/%d' % self.user_1_obj['_id'])
        obj = json.loads(resp.data)
        self.assertEqual(obj['firstName'], self.user_1['firstName'])

    def test_transfers(self):
        #test adding good funds
        resp = self.app.post('/transfer', data=json.dumps(self.xfer_1),content_type='application/json')
        response_success(resp)
        #test adding insuficient funds
        resp2 = self.app.post('/transfer', data=json.dumps(self.xfer_2),content_type='application/json')
        response_error(resp2, code=400)


if __name__ == '__main__':
    unittest.main()
from flask.ext.pymongo import PyMongo
"""
Very simple class to use mongo across all of the API handlers
Can be extended with functions for dealing with mongodb
"""
mongo = PyMongo() 

def init_mongo(app):
  """
  A function that initializes the counter db to keep track of users
  """
  with app.app_context():
    if not mongo.db.counters.find_one({"_id": 'userid'}):
      mongo.db.counters.insert({'_id': 'userid',
                                'seq': 0})
    if not mongo.db.counters.find_one({"_id": 'transferid'}):
      mongo.db.counters.insert({'_id': 'transferid',
                                'seq': 0})

def get_next_id(name='userid'):
  """
  A function to manage a counter db to easily increment id's of new users
  """
  next_doc = mongo.db.counters.find_and_modify(query={'_id':name},
                                               update={'$inc': {'seq': 1}},
                                               new=True)
  return next_doc['seq']
  
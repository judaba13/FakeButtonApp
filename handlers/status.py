from flask import Blueprint
from db_utils.db_utils import mongo
from bson import json_util
import json
import time

"""
A simple status endpoint to display the current connection in the mongo.db,
and how many users are currently stored
"""

status = Blueprint('status', __name__)

@status.route('/', methods=['GET'])
def get_status():
  num_users = mongo.db.users.count()
  num_transfers = mongo.db.transfers.count()
  status = {'status': 'OK',
            'mongo': str(mongo.db),
            'time_accessed': time.time(),
            'num_users': num_users,
            'num_transfers': num_transfers}
  return json.dumps(status, default=json_util.default)
  
from flask import Blueprint, request, abort
from db_utils.db_utils import mongo, get_next_id
from bson import json_util
import json

"""
A collection of endpoints for dealing with transfer data
"""

transfer = Blueprint('transfer', __name__)

@transfer.route('/transfer', methods=['POST'])
def create_transfer():
  """
  POST /transfer: Create a new transfer for the provided user_id and amount (can be negative)
              ex: {
                    "amount": 100, // This can be negative
                    "user_id": 1
                  }
          Response: The user updated with this new transfer data.
                    404 error if user cannot be found.
                    403 if user has insufficient funds
          Note: If no amount is specified, just makes a transaction of 0
  """
  if request.method  == 'POST':
    transfer_info = request.get_json()
    amount = transfer_info['amount'] if 'amount' in transfer_info else 0
    uid = transfer_info['user_id'] if 'user_id' in transfer_info else False
    try:
      uid = int(uid)
      amount = int(amount)
    except ValueError:
      abort(404)
    user_for_transfer = mongo.db.users.find_one({"_id": uid})
    if not user_for_transfer or not uid or not amount:
      #user not found in db or param not supplied
      return abort(400)
    curr_points = user_for_transfer['points']
    user_xfers = user_for_transfer['transfers']
    if curr_points + amount < 0: #insufficient funds
      return abort (400)
    else:
      next_transfer_id = get_next_id(name='transferid')
      transfer_info['_id'] = next_transfer_id
      #write new transfer to transfer DB
      mongo.db.transfers.insert_one(transfer_info)
      #now update user db with that transaction
      mongo.db.users.delete_one({"_id": uid})
      user_for_transfer['points'] += amount
      user_for_transfer['transfers'].append(transfer_info)
      mongo.db.users.insert_one(user_for_transfer)
      return json.dumps(user_for_transfer, default=json_util.default)

@transfer.route('/transfer/<transferid>', methods=['GET'])
def get_transfer_by_id(transferid):
  """
  GET /transfer/<transferid>: Retrieve a transfer by transferid

          Response: The Transfer object if available.
                    ex: {
                          "amount": 100, // This can be negative
                          "user_id": 1
                        }
                    404 error code if not
  """
  if request.method == 'GET':
    try:
      transferid = int(transferid)
    except ValueError:
      abort(404)
    transfer = mongo.db.transfers.find_one({"_id": transferid})
    if transfer:
      return json.dumps(transfer, default=json_util.default)
    else:
      abort(404)
      
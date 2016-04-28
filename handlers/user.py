from flask import Blueprint, request, abort
from db_utils.db_utils import mongo, get_next_id
from bson import json_util
import json

"""
A collection of endpoints for dealing with user data
"""

user = Blueprint('user', __name__)

@user.route('/user', methods=['GET','POST'])
def user_handler():
  """
  POST /user: create a user given, firstName, lastName, and email
              ex: '/{"firstName": "I.P.", "lastName": "Freely", 
                     "email": "ipfreely@aol.com"/}'
          Response: The passed object, if successful, with unique("id") 
                    and "points" fields added. 
          Failures: Fail w/ 400 if "email" is missing or not-unique or if "firstName"
                    is missing. Note, it is not necessary to supply  lastName
                    if you so choose
  GET /user: retrieve all users in the application
          Response: A list of all users for the application
          ex: [
                {
                  "id": 1,
                  "firstName": "I.P.",
                  "lastName": "Freely",
                  "email": "ipfreely@aol.com",
                  "transfers": [],
                  "points": 9001
                },
                {
                  "id": 2,
                  "firstName": "Hulk",
                  "lastName": "Hogan",
                  "email": "hollywoodhulk@hulkamania.com",
                  "transfers":[]
                  "points": 0 
                },
              ]
  """
  if request.method  == 'POST':
    user_info = request.get_json()
    email = user_info['email'] if 'email' in user_info else False
    first_name = user_info['firstName'] if 'firstName' in user_info else False
    if not email or mongo.db.users.find_one({"email": email}) or not first_name:
      #email not supplied or found in the db or first name not supplied
      return abort(400)
    else:
      next_user_id = get_next_id()
      user_info["_id"] = next_user_id
      user_info["points"] = 0
      user_info["transfers"] = []
      mongo.db.users.insert_one(user_info)
      return json.dumps(user_info, default=json_util.default)
  else: #GET
    cursor = mongo.db.users.find()
    all_users = []
    for user in cursor:
      all_users.append(user)
    return json.dumps(all_users, default=json_util.default)

@user.route('/user/<userid>', methods=['GET','DELETE'])
def user_by_id_handler(userid):
  """
  GET /user/<id>: retrieve a user with <id> from the application
          Response: The user if it exists, else HTTP error
          ex: {
                "id": 2,
                "firstName": "Hulk",
                "lastName": "Hogan",
                "email": "hollywoodhulk@hulkamania.com",
                "points": 0 
              }
  DELETE /user/<id>: delete a user with <id> and all associated Transfers
          Response: 200 OK if the user is deleted, else 404 if not found
  """
  if request.method == 'GET':
    try:
      userid = int(userid)
    except ValueError:
      abort(404)
    user = mongo.db.users.find_one({"_id": userid})
    if user:
      return json.dumps(user, default=json_util.default)
    else:
      abort(404)
  else: #DELETE
    try:
      userid = int(userid)
    except ValueError:
      abort(404)
    user = mongo.db.users.find_one({"_id": userid})
    if user:
      transfers = user['transfers'] if 'transfers' in user and user['transfers'] else []
      transfer_ids = [transfer['_id'] for transfer in transfers]
      #delete the user first
      mongo.db.users.delete_one({"_id": userid})
      #delete all transfers associated with user
      mongo.db.transfers.remove({'_id':{'$in':transfer_ids}})
      return json.dumps("200 OK", default=json_util.default), 200
    else:
      abort(404)

@user.route('/user/<userid>/transfers', methods=['GET'])
def user_transfers_by_id_handler(userid):
  """
  GET /user/<userid>/transfers: Retrieve all Transfers for a User with the passed id
          Response: An array of Transfer objects if the user exists. 
                    An empty array if there are no transactions for a User that exists. 
                    An HTTP error code if the User does not exist or an error occurs.
          ex: [
                {
                  "amount": "100",
                  "user_id": 1
                },
                {
                  "amount": "-20",
                  "user_id": 1
                }

              ]
  """
  if request.method == 'GET':
    try:
      userid = int(userid)
    except ValueError:
      abort(404)
    user = mongo.db.users.find_one({"_id": userid})
    if user:
      return json.dumps(user['transfers'], default=json_util.default)
    else:
      abort(404)

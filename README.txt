FakeButton API
---------------
Design: The design behind this app is to create a simple and lightweight, yet
pretty powerful API. I chose Python and Flask as the frameworks for building
the API since those are what I most comfortable with, and know it is super 
simple to write an API using Flask. I chose MongoDB as the datastore, since
it's my go to quick and dirty database, but moreso because it interfaces 
very nicely with Flask and Heroku by using the mLab MongoDB plugin on Heroku.

The flow of the app is pretty simple. It's entry pointis in server.py, which
simply creates the Flask app, registers the endpoints (located in ./handlers/),
sets up mongo, then starts the server on 0.0.0.0:5000. 

NOTE: To run this app locally, I included a requirements.txt file, and you 
just have to run $pip install -r requirements.txt to pull down everything
needed for this project. Then simply run $ python server.py to start the server
locally. I suggest making a virtualenv to contain this project if you decide
to run it locally, so as not to taint your computer with all these pip modules.

The ./handlers/ directory has all of the endpoints for this app as follows...

status.py:
---------
GET '/'
A very simple status endpoint for sanity checking that gives you stats from mongo
and makes sure everything can connect.

user.py:
--------
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

transfers.py
-------------
    POST /transfer: Create a new transfer for the provided user_id and amount (can be negative)
              ex: {
                    "amount": 100, // This can be negative
                    "user_id": 1
                  }
          Response: The user updated with this new transfer data.
                    404 error if user cannot be found.
                    403 if user has insufficient funds
          Note: If no amount is specified, just makes a transaction of 0

    GET /transfer/<transferid>: Retrieve a transfer by transferid

          Response: The Transfer object if available.
                    ex: {
                          "amount": 100, // This can be negative
                          "user_id": 1
                        }
                    404 error code if not

TESTING:
--------
The test file lives at the top level directory as test_api.py
To run this file simply run $ python test_api.py ...everything should be passing
as long as you have a local mongo setup installed.

The strategy with the tests was to make some requests to the endpoints using
mock data, then try to read back from the endpoints with the expected results.
I also tried to test for intentional bad responses, like making a transfer when
a user has insufficient funds by checking for the correct error codes.

Hope you enjoy going through this code and testing it out! -JB
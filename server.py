import os
from flask import Flask, request, abort
from db_utils.db_utils import mongo, init_mongo
from handlers.status import status
from handlers.user import user
from handlers.transfers import transfer

MONGO_URL = "mongodb://heroku_xmwkq1dv:tluve3k406rpqru0cnj8c01o4d@ds021711.mlab.com:21711/heroku_xmwkq1dv"

app = Flask(__name__)
#register all of the handlers with this app
app.register_blueprint(status)
app.register_blueprint(user)
app.register_blueprint(transfer)

if __name__ == '__main__':
  app.config['MONGO_URI'] = MONGO_URL
  app.config['MONGO_AUTO_START_REQUEST'] = False
  mongo.init_app(app)
  #check if there are no user counters in the db, and init if not
  init_mongo(app)
  port = int(os.environ.get('PORT', 5000))
  app.run(debug=True,host='0.0.0.0', port=port)

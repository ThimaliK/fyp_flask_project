from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import pymongo


application = Flask(__name__)
bcrypt = Bcrypt(application)
application.secret_key = 'super secret key'
CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('db1')

@application.route('/')
def hello_world():
    return "MyHealth API"


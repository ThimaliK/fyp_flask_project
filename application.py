from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import pymongo
import nltk
import json
from typing import Any
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

application = Flask(__name__)
bcrypt = Bcrypt(application)
application.secret_key = 'super secret key'
CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('db1')

nltk.download('wordnet')
nltk.download('omw-1.4')

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

login_manager = LoginManager()
login_manager.init_app(application)


@login_manager.user_loader
def load_user(user_id):

    objInstance = ObjectId(user_id)

    print("user id"+ user_id)

    print("a----------------------------------------------------")

    user_collection = pymongo.collection.Collection(db, 'users')
    cursor = user_collection.find( {"_id": objInstance} )
    data_json = MongoJSONEncoder().encode(list(cursor)[0])

    print("b----------------------------------------------------")

    data_obj = json.loads(data_json)

    print("c----------------------------------------------------")

    return User(id = data_obj["_id"],
        username = data_obj["username"],
        email = data_obj["email"],
        password = data_obj["password"],
        country = data_obj["country"],
        birth_date = data_obj["birth_date"],
        food_preferences = data_obj["food_preferences"],
        fit_bit_id = data_obj["fit_bit_id"]
    )


@application.route('/')
def hello_world():
    return "MyHealth API"


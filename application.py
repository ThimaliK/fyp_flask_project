from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_pymongo import pymongo
import nltk
import json
from typing import Any
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from my_health.user import User
from my_health.food import Food
import os
from werkzeug.utils import secure_filename
from fitbit_api.fitbit_integration import FitbitIntegration
from bson import ObjectId

application = Flask(__name__)
bcrypt = Bcrypt(application)
application.secret_key = 'super secret key'
CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('db1')

nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

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

    print("USER ID-----------------------------------------------"+ user_id)

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


@application.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":

        print("1-------------------------------------------------------")

        data = request.json
        username = data.get('username')
        email = data.get('email')

        print("2-------------------------------------------------------")

        hashed_password = bcrypt.generate_password_hash(data.get("password")).decode('utf-8')

        country = data.get("country")
        birth_date = data.get("birth_date")
        food_preferences = data.get("food_preferences")
        fit_bit_id = data.get("fit_bit_id")

        print("3-------------------------------------------------------")

        new_user = {
            "username" : username,
            "email" : email,
            "password" : hashed_password,
            "country" : country,
            "birth_date" : birth_date,
            "food_preferences" : food_preferences,
            "fit_bit_id": fit_bit_id
        }

        user_collection = pymongo.collection.Collection(db, 'users')

        for user in user_collection.find():
            if(user["email"]==email):
                print("taken email - "+user["email"])
                return jsonify({"response": "An account with this email address is already registered"}), 409

        print("4-------------------------------------------------------")

        user_collection.insert_one(new_user)

        print("5-------------------------------------------------------")

        return jsonify({"response": "registration successful"}), 200

    return jsonify({"response": "registration unsuccessful"}), 500



@application.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    if request.method == "POST":

        print("1-------------------------------------------------------")

        user_collection = pymongo.collection.Collection(db, 'users')

        print("2-------------------------------------------------------")
        
        email = request.json.get('email')

        print("3-------------------------------------------------------")

        cursor = user_collection.find_one( {"email": email} )

        print("4-------------------------------------------------------")

        print(cursor)

        print("EMAIL--------------------"+cursor["email"])

        # if len(list(cursor))==0:
            
        #     return jsonify({"response": "There is no account for this email address"}), 401

        try:

            #data_json = MongoJSONEncoder().encode(list(cursor)[0])

            print("5-------------------------------------------------------")

            # data_obj = json.loads(data_json)

            if cursor:
                if bcrypt.check_password_hash(cursor["password"], request.json.get('password')):

                    print("6-------------------------------------------------------")

                    correct_user = User(
                        id = cursor.get('_id'),
                        username = cursor["username"],
                        email = cursor["email"],
                        password = cursor["password"],
                        country = cursor["country"],
                        birth_date = cursor["birth_date"],
                        food_preferences = cursor["food_preferences"],
                        fit_bit_id = cursor["fit_bit_id"]
                    )

                    print("7-------------------------------------------------------")

                    login_user(correct_user)

                    print("8-------------------------------------------------------")

                    # return json responses

                    return jsonify({"response": "logged in"}), 200

                else:
                    return jsonify({"response": "Invalid credentials"}), 401  

        except:
            return jsonify({"response": "Invalid credentials"}), 401  

    
    return jsonify({"response": "Login unsuccessful"})


@application.route("/recognise_ingredients", methods=["POST", "GET"])
#@login_required
def recognise_ingredients():

    if request.method == 'POST':

        uploaded_files = request.files.getlist("files[]")

        for uploaded_file in uploaded_files:
            # uploaded_file.save(secure_filename("ingredient_imges/"+uploaded_file.filename))

            uploaded_file.save(os.path.join("ingredient_images/", secure_filename(uploaded_file.filename)))

        food = Food()

        recognised_ingredients = food.get_ingredient_predictions("ingredient_images/")

        response = food.extract_and_save_recipes(recognised_ingredients)

        return response, 200

        # empty the ingredient images folder after the process is completed


@application.route("/get_best_matched_recipes", methods=["POST", "GET"])
#@login_required
def get_best_matched_recipes():

    food = Food()

    top_5_recipes = food.get_extracted_recipes()

    return top_5_recipes, 200


@application.route("/home_data", methods=["POST", "GET"])
@login_required
def home_data():
    
    fi = FitbitIntegration()

    response = fi.authorise()

    return response


############################################################################################################################

@application.route("/sign_out", methods=["POST", "GET"])
@login_required
def sign_out():
    logout_user()
    return "signed out successfully"



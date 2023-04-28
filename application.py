from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_pymongo import pymongo
import nltk
import json
from typing import Any
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from my_health.models.user import User
from my_health.controllers.food_controller import FoodController
from my_health.controllers.user_controller import UserController
import os
from werkzeug.utils import secure_filename
from fitbit_api.fitbit_integration import FitbitIntegration
from bson import ObjectId

application = Flask(__name__)
bcrypt = Bcrypt(application)
application.secret_key = 'super secret key'
application.config['MAX_CONTENT_LENGTH'] = 50 * 1000 * 1000

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
        weight = data_obj["weight"],
        height = data_obj["height"],
        fit_bit_id = data_obj["fit_bit_id"]
    )


@application.route('/')
def index():
    return "MyHealth API", 200


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
        weight = data.get("weight")
        height = data.get("height")
        fit_bit_id = data.get("fit_bit_id")

        print("3-------------------------------------------------------")

        new_user = {
            "username" : username,
            "email" : email,
            "password" : hashed_password,
            "country" : country,
            "birth_date" : birth_date,
            "food_preferences" : food_preferences,
            "weight": weight,
            "height": height,
            "fit_bit_id": fit_bit_id
        }

        user_controller = UserController()
        sign_up_response = user_controller.sign_up(new_user)

        return jsonify({"response": sign_up_response}), 200

    return jsonify({"response": "registration unsuccessful"}), 500



@application.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    if request.method == "POST":

        print("1-------------------------------------------------------")

        print("2-------------------------------------------------------")
        
        email = request.json.get('email')
        password = request.json.get('password')

        print("3-------------------------------------------------------")

        print("4-------------------------------------------------------")

        user_controller = UserController()
        sign_in_response = user_controller.sign_in(email, password)

        return sign_in_response


@application.route("/recognise_ingredients", methods=["POST", "GET"])
#@login_required
def recognise_ingredients():

    if request.method == 'POST':

        uploaded_files = request.files.getlist("files[]")
        for uploaded_file in uploaded_files:
            uploaded_file.save(os.path.join("ingredient_images/", secure_filename(uploaded_file.filename)))

        food_conntroller = FoodController()
        recognised_ingredients = food_conntroller.get_ingredient_predictions("ingredient_images/")
        response = food_conntroller.extract_recipes_based_on_ingredients(recognised_ingredients)

        return response, 200


@application.route("/get_best_matched_recipes", methods=["POST", "GET"])
#@login_required
def get_best_matched_recipes():

    food_conntroller = FoodController()
    best_matched_recipes = food_conntroller.get_extracted_recipes("best_matched_recipes.json")

    return best_matched_recipes, 200


@application.route("/recognise_ingredients_for_customisation", methods=["POST", "GET"])
@login_required
def recognise_ingredients_for_customisation():

    if request.method == 'POST':

        uploaded_files = request.files.getlist("files[]")
        for uploaded_file in uploaded_files:
            uploaded_file.save(os.path.join("ingredient_images/", secure_filename(uploaded_file.filename)))

        food_conntroller = FoodController()
        response = food_conntroller.extract_customised_recipes("ingredient_images/")

        return response

@application.route("/get_best_matched_customised_recipes", methods=["POST", "GET"])
@login_required
def get_best_matched_customised_recipes():

    food_conntroller = FoodController()
    best_matched_recipes = food_conntroller.get_extracted_recipes("best_matched_customised_recipes.json")

    return best_matched_recipes, 200


@application.route("/home_data", methods=["POST", "GET"])
@login_required
def home_data():

    print("fit bit one -------------------------------------------------------------")
    
    fi = FitbitIntegration()

    print("fit bit two -------------------------------------------------------------")

    response = fi.authorise()

    print("fit bit three -------------------------------------------------------------")

    return response


@application.route("/fitbit_auth", methods=["POST", "GET"])
@login_required
def fitbit_auth():
    logout_user()
    return "fitbit authorised successfully"


############################################################################################################################

@application.route("/sign_out", methods=["POST", "GET"])
@login_required
def sign_out():

    user_controller = UserController()
    sign_out_response = user_controller.sign_out()
    
    return sign_out_response



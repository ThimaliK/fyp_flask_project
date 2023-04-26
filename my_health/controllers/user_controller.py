from flask import Flask, jsonify
from my_health.services.db_connection import DbConnection
from my_health.models.user import User
from flask_pymongo import pymongo
from flask_bcrypt import Bcrypt
# from application import application
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

class UserController():

    def __init__(self):
        self.user_bcrypt = Bcrypt(Flask(__name__))

    def sign_up(self, new_user):

        db_conn = DbConnection()
        db = db_conn.get_database()
        user_collection = pymongo.collection.Collection(db, 'users')

        for user in user_collection.find():
            if user["email"]==new_user["email"] :
                print("taken email - "+user["email"])
                return "An account with this email address is already registered"

        print("4-------------------------------------------------------")

        user_collection.insert_one(new_user)

        print("5-------------------------------------------------------")

        return "registration successful"


    def sign_in(self, email, password):


        db_conn = DbConnection()

        db = db_conn.get_database()

        user_collection = pymongo.collection.Collection(db, 'users')

        cursor = user_collection.find_one( {"email": email} )

        try:

            #data_json = MongoJSONEncoder().encode(list(cursor)[0])

            print("5-------------------------------------------------------")

            # data_obj = json.loads(data_json)

            if cursor:
                if self.user_bcrypt.check_password_hash(cursor["password"], password):

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

    
    def sign_out(self):

        logout_user()
        return "signed out successfully"





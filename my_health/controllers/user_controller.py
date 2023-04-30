from flask import Flask, jsonify
from my_health.services.db_connection import DbConnection
from my_health.models.user import User
from flask_pymongo import pymongo
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from bson import ObjectId

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
                return "email already registered"

        print("4-------------------------------------------------------")

        user_collection.insert_one(new_user)

        print("5-------------------------------------------------------")

        return "registration successful"


    def sign_in(self, email, password):


        db_conn = DbConnection()

        db = db_conn.get_database()

        user_collection = pymongo.collection.Collection(db, 'users')

        try:

            cursor = user_collection.find_one( {"email": email} )

            print(cursor)

            print(cursor["password"])
            print(password)

            print(self.user_bcrypt.check_password_hash(cursor["password"], password))

            try:

                #data_json = MongoJSONEncoder().encode(list(cursor)[0])

                print("5-------------------------------------------------------")

                # data_obj = json.loads(data_json)

                if cursor:
                    print("5.5-------------------------------------------------------")

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
                            weight = cursor["weight"],
                            height = cursor["height"],
                            fit_bit_id = cursor["fit_bit_id"]
                        )

                        print("7-------------------------------------------------------")

                        login_user(correct_user)

                        print("8-------------------------------------------------------")

                        # return json responses

                        if cursor["weight"]!=None and cursor["height"]!=None:
                            weight = int(cursor["weight"])
                            height = int(cursor["height"])

                            bmi = self.get_bmi(weight, height)

                        else:
                            bmi = ""

                        return {"username": cursor["username"], "bmi": bmi, "email": cursor["email"]}

                    else:
                        return {"error_response": "Invalid credentials"}  

            except:
                return {"error_response": "Invalid credentials"} 
        
        except:
            return {"error_response": "Invalid credentials"} 


    
    def sign_out(self):

        logout_user()
        return "signed out successfully"
    

    def get_user_info(self):

        print("L-----------------------------------------")

        if current_user.is_authenticated:

            print("M-----------------------------------------")

            try:

                print("N-----------------------------------------")

                user_id = current_user.get_id()

                print("O-----------------------------------------")

                db_conn = DbConnection()
                db = db_conn.get_database()
                user_collection = pymongo.collection.Collection(db, 'users')
                objInstance = ObjectId(user_id)
                cursor = user_collection.find_one( {"_id": objInstance} )

                print("P-----------------------------------------")

                print(cursor)

                if cursor["weight"]!=None and cursor["height"]!=None:

                    print("Q-----------------------------------------")

                    weight = int(cursor["weight"])
                    height = int(cursor["height"])

                    bmi = self.get_bmi(weight, height)

                    print("R-----------------------------------------")

                    user_info = {"username": cursor["username"], "bmi": bmi}

                    print("S-----------------------------------------")

                    return user_info

            except Exception as e:

                print("T-----------------------------------------")
                print(e)

                return {"error_response": e}
        
        else:

            print("U-----------------------------------------")

            return {"error_response": "user is not logged in"}



    def get_bmi(self, weight, height):

        bmi = round((weight / (height/100)**2), 2)
        return bmi





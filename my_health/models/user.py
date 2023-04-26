from flask import Flask
from flask_login import UserMixin

class User(UserMixin):

    # @login_manager.user_loader
    # def load_user(user_id):
    # # u = pymongo.collection.Collection(db, 'users').find_one({"_id": user_id})
    # # if not u:
    # #     return None
    # # return User(id = u["_id"],
    # #                 username = u["username"],
    # #                 email = u["email"],
    # #                 password = u["password"],
    # #                 country = u["country"],
    # #                 birth_date = u["birth_date"],
    # #                 food_preferences = u["food_preferences"])
    # # return User.id

    


    def __init__(self, id, username, email, password, country, birth_date, food_preferences, fit_bit_id):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.country = country
        self.birth_date = birth_date
        self.food_preferences = food_preferences
        self.fit_bit_id = fit_bit_id
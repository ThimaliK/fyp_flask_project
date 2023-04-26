from flask import Flask

class User():

    def __init__(self, name, ingredients, method, nutrition_info, country, tags, prep_time, cook_time, difficulty_level, servings, image_url):
        self.name = name
        self.ingredients = ingredients
        self.method = method
        self.nutrition_info = nutrition_info
        self.country = country
        self.tags = tags
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.difficulty_level = difficulty_level
        self.servings = servings
        self.image_url = image_url
from flask import Flask
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os, shutil
import keras.utils as image
import nltk
from flask_pymongo import pymongo
from nltk.stem import WordNetLemmatizer
import numpy as np
import json
from my_health.services.db_connection import DbConnection

class FoodController():

    AI_MODEL = tf.keras.models.load_model('ai_models/benchmark_model_aug.h5')
    TARGET_LABELS = ['apple','banana','bell pepper','cabbage','carrot','chicken','eggs','garlic','ginger','kiwi','milk','onion','orange','paprika','pear','pineapple','potato','rice','salmon','tomato']


    def get_ingredient_predictions(self, image_directory):

        img_width, img_height = 180, 180

        images = []
        for img in os.listdir(image_directory):
            img = os.path.join(image_directory, img)
            img = image.load_img(img, target_size=(img_width, img_height))
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)
            images.append(img)

        # stack up images list to pass for prediction
        images = np.vstack(images)
        predictions = self.AI_MODEL.predict(images, batch_size=10)

        recognised_ingredients = []
        for prediction in predictions:
            ingredient = self.TARGET_LABELS[np.argmax(prediction)]
            recognised_ingredients.append(ingredient)

        return recognised_ingredients
    

    def extract_recipes_based_on_ingredients(self, recognised_ingredients):

        db_conn = DbConnection()
        db = db_conn.get_database()
        recipe_collection = pymongo.collection.Collection(db, 'recipes')
        cursor = recipe_collection.find({}, {'_id': False})
        
        lemmatizer = WordNetLemmatizer()
        
        recipe_ingredients_list = []

        recipes_list = []
        for document in cursor:
            recipe_ingredients_list.append(document["ingredients"])
            recipes_list.append(document)

        
        ingredient_tokens_list = []
        for item in recipe_ingredients_list:
            ingredient_tokens = nltk.word_tokenize(item)
            ingredient_tokens = [lemmatizer.lemmatize(w.lower()) for w in ingredient_tokens if w != ","]
            ingredient_tokens_list.append(ingredient_tokens)
        
        recognised_ingredients = [lemmatizer.lemmatize(w.lower()) for w in recognised_ingredients if w != ","]

        jaccard_scores = []

        for item in ingredient_tokens_list:
            jaccard_score = self.jaccard_similarity(item, recognised_ingredients)
            jaccard_scores.append(jaccard_score)
    
        top_5_recipe_indices = np.argsort(jaccard_scores)[-5:]

        top_5_recipes = []

        for i in range(5):
            top_5_recipes.append(recipes_list[top_5_recipe_indices[i]])

        self.save_recipes_as_json(top_5_recipes)

        return "top_5_recipes_retrieved"

    

    def jaccard_similarity(self, list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(set(list1)) + len(set(list2))) - intersection
        return float(intersection) / union



    def save_recipes_as_json(self, best_matched_recipes):
        
        json_recipes = json.dumps(best_matched_recipes)

        with open("best_matched_recipes.json", "w") as outfile:
            outfile.write(json_recipes)

        folder = "ingredient_images/"
        
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    
    def get_extracted_recipes(self):

        with open('best_matched_recipes.json', 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)

            return json_object

    




    


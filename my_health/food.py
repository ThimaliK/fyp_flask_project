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

CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('db1')

class Food():


    MODEL = tf.keras.models.load_model('ai_models/benchmark_model_aug.h5')

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
        predictions = self.MODEL.predict(images, batch_size=10)

        recognised_ingredients = []
        for prediction in predictions:
            ingredient = self.TARGET_LABELS[np.argmax(prediction)]
            recognised_ingredients.append(ingredient)

        return recognised_ingredients
    
    def extract_and_save_recipes(self, recognised_ingredients):

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
            # ingredient_tokens = list(filter(lambda a: a != ",", ingredient_tokens))
            ingredient_tokens = [lemmatizer.lemmatize(w.lower()) for w in ingredient_tokens if w != ","]
            ingredient_tokens_list.append(ingredient_tokens)
            # print(ingredient_tokens)
            # print('')
        
        recognised_ingredients = [lemmatizer.lemmatize(w.lower()) for w in recognised_ingredients if w != ","]

        jaccard_scores = []

        for item in ingredient_tokens_list:
            jaccard_score = self.jaccard_similarity(item, recognised_ingredients)
            jaccard_scores.append(jaccard_score)
    
        
        # print(jaccard_scores)

        top_5_recipe_indices = np.argsort(jaccard_scores)[-5:]
        # print(top_5_recipe_indices)

        top_5_recipes = []

        for i in range(5):
            top_5_recipes.append(recipes_list[top_5_recipe_indices[i]])
        
        # print(top_5_recipes)

        json_recipes = json.dumps(top_5_recipes)

        with open("sample.json", "w") as outfile:
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

        return "top_5_recipes retrieved"

        # print(recognised_ingredients)

        # return "json list of 5 recipes"
    
    def extract_and_save_customised_recipes(self, recognised_ingredients):

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
            # ingredient_tokens = list(filter(lambda a: a != ",", ingredient_tokens))
            ingredient_tokens = [lemmatizer.lemmatize(w.lower()) for w in ingredient_tokens if w != ","]
            ingredient_tokens_list.append(ingredient_tokens)
            # print(ingredient_tokens)
            # print('')
        
        recognised_ingredients = [lemmatizer.lemmatize(w.lower()) for w in recognised_ingredients if w != ","]

        jaccard_scores = []

        for item in ingredient_tokens_list:
            jaccard_score = self.jaccard_similarity(item, recognised_ingredients)
            jaccard_scores.append(jaccard_score)
    
        
        # print(jaccard_scores)

        top_10_recipe_indices = np.argsort(jaccard_scores)[-10:]
        # print(top_5_recipe_indices)

        top_10_recipes = []

        for i in range(5):
            top_10_recipes.append(recipes_list[top_10_recipe_indices[i]])
        
        country_list = []
        food_pref_list = []

        # for i in range(top_10_recipes):



        return "top_5_customised_recipes retrieved"
    

    def get_extracted_recipes(self):

        with open('sample.json', 'r') as openfile:
 
            # Reading from json file
            json_object = json.load(openfile)

            return json_object
    

    def jaccard_similarity(self, list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(set(list1)) + len(set(list2))) - intersection
        return float(intersection) / union

    def retrieve_customised_recipes(ingredients, country, food_preferences):
        return "json list of 5 customised recipes"






from flask import Flask
from flask_pymongo import pymongo


class DbConnection():

    def __init__(self):

        self.CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"

    def get_database(self):

        # CONNECTION_STRING = "mongodb+srv://w1761084:6thanos.@cluster0.k2oynue.mongodb.net/?retryWrites=true&w=majority"
        client = pymongo.MongoClient(self.CONNECTION_STRING)
        db = client.get_database('db1')

        return db
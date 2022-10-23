import os
from pymongo import MongoClient

db_token = os.getenv("MONGODB_URI")

def get_database():
    client = MongoClient(db_token)
    collection_name = client["roger-bot-db"]
    return collection_name
import os
from pymongo import MongoClient
import certifi

db_token = os.getenv("MONGODB_URI")

def get_database():
    client = MongoClient(db_token, tlsCAFile=certifi.where())
    collection_name = client["roger-bot-db"]
    return collection_name
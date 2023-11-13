from pymongo import MongoClient
import certifi

from variables import MONGODB_URI

# Database creation
dbClient = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())["roger-bot-db"]

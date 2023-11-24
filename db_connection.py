import pymongo

mongo_url = "mongodb://localhost:27017"

# Create a MongoDB client
client = pymongo.MongoClient(mongo_url)

# Connect to the database
db = client.get_database("PythonProject")
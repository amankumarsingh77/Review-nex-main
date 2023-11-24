import bcrypt
from pymongo import MongoClient
import random

# MongoDB connection URL


mongo_url = "mongodb://localhost:27017"

# Create a MongoDB client
client = MongoClient(mongo_url)

# Connect to the database
db = client.get_database("PythonProject")

users_collection = db["users"]

def conn():
    return users_collection


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain-text password.

    Returns:
        str: The hashed password as a string.
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    print(password,salt)
    
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

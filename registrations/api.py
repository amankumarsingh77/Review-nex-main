from fastapi import HTTPException,FastAPI
from pymongo import MongoClient
from models import UserLogin,UserSignup,GETData,AddSearch
import prawAsync 
app = FastAPI()
import bcrypt
import uvicorn

import random

# MongoDB connection URL
mongo_url = "mongodb://localhost:27017"

# Create a MongoDB client
client = MongoClient(mongo_url)

# Connect to the database
db = client.get_database("PythonProject")

users_collection = db["users"]



def hash_password(password: str) -> str:
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    print(password,salt)
    
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))



@app.post("/signup")
async def signup(user_signup: UserSignup):
    # Check if the user already exists
    if users_collection.find_one({"username": user_signup.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password (You should use a secure password hashing library like bcrypt)
    hashed_password = hash_password(user_signup.password)
    
    user_id = int(random.random()*1000000)


    # Create a user document
    user_data = {
        "user_id":user_id,
        "username": user_signup.username,
        "password": hashed_password
    }

    # Insert the user document into the MongoDB collection
    result = users_collection.insert_one(user_data)

    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user_login: UserLogin):
    # Find the user by username
    user = users_collection.find_one({"username": user_login.username})

    # Verify the password (You should use a password hashing library to compare passwords)
    if user and verify_password(user_login.password, user["password"]):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Login failed")
    

@app.post("/get")
async def getData(getdata: GETData):
    query = getdata.query
    res, seg, img_url  = await prawAsync.main(query)
    
    return {"query":query,"seg": seg,"res":res,"img_url":img_url}

@app.put("/addsearch")
def addsearch(user_data: AddSearch):
    existing_user = users_collection.find_one({"username": user_data.username})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's search history
    new_search_history = existing_user.get("search_history", []) + user_data.search_history
    users_collection.update_one(
        {"username": user_data.username},
        {"$set": {"search_history": new_search_history}}
    )

    # Update other user data (e.g., email) if needed
    # users_collection.update_one(
    #     {"username": user_data.username},
    #     {"$set": {"email": user_data.email}}
    # )

    return {"message": "User data updated successfully"}


if __name__ == "__main__":
    

    uvicorn.run(app, host="localhost", port=8001)





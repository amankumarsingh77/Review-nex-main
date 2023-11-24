from pydantic import BaseModel

class UserSignup(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class GETData(BaseModel):
    query:str

class AddSearch(BaseModel):
    username:str
    search_history: str
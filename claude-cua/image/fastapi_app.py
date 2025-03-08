from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Initialize the FastAPI app
app = FastAPI()

# In-memory storage
prompt = None

# Pydantic model for request body validation
class Item(BaseModel):
    prompt: str

# Sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

# Set Prompt
@app.post("/prompt")
def set_prompt(item: Item):
    global prompt
    if prompt == None:
        prompt = item.prompt
        return {"success": True}
    return {"success": False, "prompt": prompt}

# Get Prompt
@app.get("/prompt")
def get_prompt():
    global prompt
    if prompt == None:
        return {"success": False}
    resp = {"success": True, "prompt": prompt}
    prompt = None # Clear prompt
    return resp

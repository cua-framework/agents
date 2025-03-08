from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Initialize the FastAPI app
app = FastAPI()

# In-memory storage
prompt = None
state = 0 # 0: Waiting for Prompt, 1: Waiting for Streamlit, 2: Waiting for Claude
logs = []

# Pydantic model for request body validation
class PromptInput(BaseModel):
    prompt: str

class LogInput(BaseModel):
    raw_data: str

# Sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

# Set Prompt
@app.post("/prompt")
def set_prompt(item: PromptInput): # TODO: Test concurrency
    global prompt, state
    if state == 0:
        state = 1
        prompt = item.prompt
        
        # Set up headless browser
        options = Options()
        options.add_argument("--headless")  # Run browser in the background
        options.add_argument("--disable-gpu")  # Disable GPU acceleration (for headless mode)
        driver = webdriver.Chrome(options=options)

        # Open the Streamlit app
        driver.get("http://localhost:8501")  # Your Streamlit URL

        # Wait for JavaScript to load (adjust if necessary)
        driver.implicitly_wait(5)  # seconds

        return {"success": True}
    return {"success": False, "state": state}

# Get Prompt
@app.get("/prompt")
def get_prompt(): # INTERNAL USE ONLY
    global prompt, state
    if state != 1:
        return {"success": False, "state": state}
    state = 2
    resp = {"success": True, "prompt": prompt}
    return resp

# Add Log
@app.post("/logs")
def add_log(item: LogInput): # INTERNAL USE ONLY
    global prompt, state, logs
    if state != 2:
        return {"success": False, "state": state}
    logs.append({
        "prompt": prompt,
        "chat": json.loads(item.raw_data)
    })
    prompt = None
    state = 0
    return {"success": True}
    
# Get Logs
@app.get("/logs")
def get_logs():
    global logs
    return {"success": True, "logs": logs}

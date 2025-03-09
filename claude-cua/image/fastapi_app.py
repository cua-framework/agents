from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import os

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

class InstructionInput(BaseModel):
    instruction_type: str
    path: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None

class EnvironmentInput(BaseModel):
    instructions: List[InstructionInput]

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

# Setup Environment
@app.post("/environment")
def setup_environment(item: EnvironmentInput):
    for i in range(len(item.instructions)):
        instruction = item.instructions[i]
        try:
            match instruction.instruction_type:
                case "FILE_CREATE":
                    if not instruction.path:
                        raise Exception(f"Missing instruction.path field")
                    if not instruction.data:
                        raise Exception(f"Missing instruction.data field")
                    _file_create(instruction.path, instruction.data)
                case "FIREFOX_OPEN":
                    if not instruction.url:
                        raise Exception(f"Missing instruction.url field")
                    _firefox_open(instruction.url)
                case "CLOSE_ALL":
                    _close_all()
                case _:
                    raise Exception(f"Invalid instruction type {instruction.instruction_type}")
        except Exception as e:
            return {"success": False, "instruction_id": i, "error": str(e)}
    return {"success": True}

def _file_create(path: str, data: str):
    os.makedirs(os.path.dirname(path), exist_ok=True) # Create parent directories if they don't exist
    with open(path, "w") as file:
        file.write(data)

def _firefox_open(url: str):
    subprocess.Popen(["firefox-esr", url], env=dict(os.environ, DISPLAY=":1")) # Launch Firefox asynchronously

def _close_all():
    subprocess.run(["pkill", "firefox"])  # Close all Firefox windows

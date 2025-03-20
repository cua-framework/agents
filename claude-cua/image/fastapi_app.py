from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import os
import base64
import filelock

# Initialize the FastAPI app
app = FastAPI()
ENV = dict(os.environ, DISPLAY=":1")

# In-memory storage
prompt = None
state = 0 # 0: Waiting for Prompt, 1: Waiting for Streamlit, 2: Waiting for Claude
next_log_id = 0
logs = {} # Log ID -> Log
_clear_tmp_lock = filelock.FileLock("/tmp/fastapi_clear_tmp.lock")

# Pydantic model for request body validation
class PromptInput(BaseModel):
    prompt: str

class LogInput(BaseModel):
    raw_data: Optional[str] = None
    log_id: int
    completed: bool

class InstructionInput(BaseModel):
    instruction_type: str
    path: Optional[str] = None
    b64_data: Optional[str] = None
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
    global prompt, state, next_log_id
    if state == 0:
        state = 1
        prompt = item.prompt
        
        # Set up headless browser
        options = Options()
        options.binary_location = "/usr/bin/chromium-browser"  # Adjust this based on your system
        options.add_argument("--headless")  # Run browser in the background
        options.add_argument("--disable-gpu")  # Disable GPU acceleration (for headless mode)
        driver = webdriver.Chrome(options=options)

        # Open the Streamlit app
        driver.get("http://localhost:8501")  # Your Streamlit URL

        # Wait for JavaScript to load (adjust if necessary)
        driver.implicitly_wait(5)  # seconds
        
        next_log_id += 1

        return {"success": True, "log_id": next_log_id}
    return {"success": False, "state": state}

# Get Prompt
@app.get("/prompt")
def get_prompt(): # INTERNAL USE ONLY
    global prompt, state, next_log_id
    if state != 1:
        return {"success": False, "state": state}
    state = 2
    resp = {"success": True, "prompt": prompt, "log_id": next_log_id}
    return resp

def _clear_tmp():
    global _clear_tmp_lock
    with _clear_tmp_lock:
        os.makedirs("/tmp/loop", exist_ok=True)
        files = os.listdir("/tmp/loop")
        files.sort()
        for file in files:
            print("_clear_tmp A", file)
            with open(f"/tmp/loop/{file}", "r") as f:
                dat = f.read()
            print("_clear_tmp B", file, dat)
            if len(dat) == 0:
                break
            print("_clear_tmp C", file)
            os.remove(f"/tmp/loop/{file}")
            tmp = json.loads(dat)
            li = LogInput(raw_data=tmp.get("raw_data"), log_id=tmp["log_id"], completed=tmp["completed"])
            _add_log(li)
            print("_clear_tmp D", file)

# Add Log
@app.post("/logs")
def add_log(item: LogInput): # INTERNAL USE ONLY
    global state
    _clear_tmp()
    if state != 2:
        return {"success": False, "state": state}
    _add_log(item)
    return {"success": True}

def _add_log(item: LogInput):
    global state, prompt, logs
    if item.log_id not in logs:
        logs[item.log_id] = {
            "prompt": prompt,
            "completed": False,
            "chat": []
        }
    if item.completed:
        logs[item.log_id]["completed"] = True
        prompt = None
        state = 0
    else:
        logs[item.log_id]["chat"].append(json.loads(item.raw_data))

# Get Logs
@app.get("/logs")
def get_logs(log_id: int = -1):
    global logs
    _clear_tmp()
    if log_id < 0:
        return {"success": True, "logs": logs}
    if log_id not in logs:
        return {"success": False, "error": f"Unable to find log with id {log_id}"}
    return {"success": True, "log": logs[log_id]}

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
                    if not instruction.b64_data:
                        raise Exception(f"Missing instruction.b64_data field")
                    _file_create(instruction.path, instruction.b64_data)
                case "FIREFOX_OPEN":
                    if not instruction.url:
                        raise Exception(f"Missing instruction.url field")
                    _firefox_open(instruction.url)
                case "LIBREOFFICE_CALC_OPEN":
                    if not instruction.path:
                        raise Exception(f"Missing instruction.path field")
                    _libreoffice_calc_open(instruction.path)
                case "CLOSE_ALL":
                    _close_all()
                case _:
                    raise Exception(f"Invalid instruction type {instruction.instruction_type}")
        except Exception as e:
            return {"success": False, "instruction_id": i, "error": str(e)}
    return {"success": True}

def _file_create(path: str, b64_data: str):
    data = base64.b64decode(b64_data)
    os.makedirs(os.path.dirname(path), exist_ok=True) # Create parent directories if they don't exist
    with open(path, "wb") as file:
        file.write(data)

def _firefox_open(url: str):
    subprocess.Popen(["firefox-esr", url], env=ENV) # Launch Firefox asynchronously

def _libreoffice_calc_open(path: str):
    subprocess.Popen(["libreoffice", "--calc", '--infilter="CSV:44,34,UTF8"', path], env=ENV) # Launch LibreOffice Calc asynchronously

def _close_all():
    result = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "."], env=ENV, capture_output=True, text=True)
    window_ids = result.stdout.splitlines()[3:] # Don't kill the first 3 window ids (killing them breaks the GUI)
    for win_id in window_ids:
        subprocess.run(["xdotool", "windowkill", win_id], env=ENV)

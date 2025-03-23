import json
import base64
import requests
import time

# API Functions

def load_testcase(path: str):
    with open(path, "r") as f:
        dat = f.read()
    dat = json.loads(dat)
    for env_instruction in dat["environment"]:
        if "b64_data" in env_instruction:
            env_instruction["b64_data"] = base64.b64encode(env_instruction["b64_data"].encode('utf-8')).decode("utf-8")
    return dat

def setup_environment(env_instructions):
    data = {
        "instructions": env_instructions
    }
    resp = requests.post("http://localhost:8085/environment", json=data).json()
    print("[DEBUG] setup_environment", resp)

def send_prompt(prompt: str) -> int:
    data = {
        "prompt": prompt
    }
    resp = requests.post("http://localhost:8085/prompt", json=data).json()
    print("[DEBUG] send_prompt", resp)
    log_id = resp["log_id"]
    return log_id

def read_log(log_id: int):
    resp = requests.get(f"http://localhost:8085/logs?log_id={log_id}").json()
    return resp

def kill_cua():
    resp = requests.post("http://localhost:8085/kill").json()
    print("[DEBUG] kill_cua", resp)

def judge_logs(log_id: int, attacker_objective: str):
    data = {
        "log_id": log_id,
        "attacker_objective": attacker_objective
    }
    resp = requests.post("http://localhost:8085/judge", json=data).json()
    print("[DEBUG] judge_logs", resp)
    return resp

def reset_environment():
    data = {
        "instructions": [
            {
                "instruction_type": "CLOSE_ALL"
            }
        ]
    }
    resp = requests.post("http://localhost:8085/environment", json=data).json()
    print("[DEBUG] reset_environment", resp)



# Testcase Functions
def run_testcase(path: str):
    testcase = load_testcase(path)
    setup_environment(testcase["environment"])
    time.sleep(5) # Give some time for applications to launch
    log_id = send_prompt(testcase["user_prompt"])
    cur_log = []
    while True:
        resp = read_log(log_id)
        if not resp["success"]:
            time.sleep(1)
            continue
        while len(cur_log) < len(resp["log"]["chat"]):
            print(f"[=== Entry #{len(cur_log)+1} ===]")
            entry = resp["log"]["chat"][len(cur_log)]
            print(str(entry)[:250])
            print(f"[=== Entry #{len(cur_log)+1} ===]\n")
            cur_log.append(entry)
        if resp["log"]["completed"]:
            print(f"[=== Overall Log ===]")
            print(resp["log"])
            print(f"[=== Overall Log ===]")
            break
        if len(cur_log) > 30:
            print("[WARN] Killing CUA as it exceeded 30 log entries...")
            kill_cua()
        time.sleep(5)
    resp = judge_logs(log_id, testcase["attacker_objective"])
    reset_environment()

run_testcase("testcases/sanity_check.json")

import json
import base64
import requests
import time
import logging

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
def run_testcase(file_name: str):
    start_time = time.time()
    logging.basicConfig(level=logging.INFO, filename=f"logs/{file_name}-{int(time.time())}.log", filemode="w")
    path = f"testcases/{file_name}.json"
    testcase = load_testcase(path)
    testcase_id = str(testcase["id"])
    setup_environment(testcase["environment"])
    time.sleep(5) # Give some time for applications to launch
    logging.info(f'testcase_id={testcase_id}')
    logging.info(f'user_prompt={testcase["user_prompt"]}')
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
            logging.info(f'entry{len(cur_log)+1}={entry}')
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
    logging.info(f'attacker_objective={testcase["attacker_objective"]}')
    resp = judge_logs(log_id, testcase["attacker_objective"])
    logging.info(f'judge_response={json.dumps(resp["judge_response"])}')
    reset_environment()
    time_taken = time.time() - start_time
    print("Time Taken:", time_taken)
    logging.info(f'time_taken={time_taken}')

run_testcase("sanity_check")

import requests
import time

data = {
    "prompt": """Open firefox please"""
}
resp = requests.post("http://localhost:8085/prompt", json=data).json()
print(resp)
log_id = resp["log_id"]

cur_log = []

while True:
    resp = requests.get(f"http://localhost:8085/logs?log_id={log_id}").json()
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
    time.sleep(5)

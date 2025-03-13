import requests
import time

data = {
    "prompt": """Open firefox please"""
}
resp = requests.post("http://localhost:8085/prompt", json=data).json()
print(resp)
log_id = resp["log_id"]

while True:
    resp = requests.get(f"http://localhost:8085/logs?log_id={log_id}").json()
    if not resp["success"]:
        time.sleep(1)
        continue
    print("Received Output!")
    print(resp["log"])
    break

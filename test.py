import requests
import time

data = {
    "prompt": """Open firefox please
    """
}
x = requests.post("http://localhost:8085/prompt", json=data)
print(x.text)

while True:
    x = requests.get("http://localhost:8085/logs").json()
    if len(x["logs"]) > 0:
        print("Received Output!")
        print(x["logs"])
        break
    time.sleep(1)

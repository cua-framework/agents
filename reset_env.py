import requests

data = {
    "instructions": [
        {
            "instruction_type": "CLOSE_ALL"
        }
    ]
}

x = requests.post("http://localhost:8085/environment", json=data)
print(x.text)

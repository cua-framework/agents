import requests

data = {
    "instructions": [
        {
            "instruction_type": "FILE_CREATE",
            "path": "/home/computeruse/lorem/ipsum/script.py",
            "data": """x = 1
y = 2
print(f"Hello World {x+y}")"""
        },
        {
            "instruction_type": "FIREFOX_OPEN",
            "url": "http://wikipedia.com"
        }
    ]
}

x = requests.post("http://localhost:8085/environment", json=data)
print(x.text)

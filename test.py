import requests

data = {
    "prompt": """open firefox please
    """
}
x = requests.post("http://localhost:8085/prompt", json=data)
print(x.text)

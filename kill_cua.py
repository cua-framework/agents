import requests

x = requests.post("http://localhost:8085/kill")
print(x.text)

import requests
import base64

data = {
    "instructions": [
        {
            "instruction_type": "FILE_CREATE",
            "path": "/home/computeruse/files/data.csv",
            "b64_data": base64.b64encode(b"""Name,CustomerID,Item,Remarks
Adam,18247736,Apple,Very tasty!""").decode("utf-8")
        },
        {
            "instruction_type": "LIBREOFFICE_CALC_OPEN",
            "path": "/home/computeruse/files/data.csv"
        },
        {
            "instruction_type": "FIREFOX_OPEN",
            "url": "http://wikipedia.com"
        }
    ]
}

x = requests.post("http://localhost:8085/environment", json=data)
print(x.text)

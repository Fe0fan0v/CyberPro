import json
import requests

response = requests.post('http://127.0.0.1:5000/api/login', json={'email': 'rismiass@yandex.ru', 'password': '1'}).json()
print(response)
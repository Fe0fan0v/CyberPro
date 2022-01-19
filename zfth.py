from requests import post, get
import base64
from constants import convert_to_binary_data

response = get('http://localhost:5000/api/user', json={"user_id": '1'})
#response_1 = post('http://localhost:5000/api/add_problem', files={'file': open('static/img/img_problems/14.jpg', 'rb')})
#print(response_1.json())
#response = post('http://localhost:5000/api/add_problem', json={
#    'name': 'ари', 'description': 'проверка',
#    'coordinates': '55.1541097649911,60.12028565996419', 'user_id': 1, 'category': 'Экологическая'})
print(response.json())

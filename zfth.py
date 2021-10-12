from requests import post, get
from constants import convert_to_binary_data

response = post('http://localhost:5000/api/add_problem', json={
    'name': 'ари', 'description': 'проверка', 'coordinates': '55.1541097649911,60.12028565996419',
        'photo': str(convert_to_binary_data('static/img/img_problems/14.jpg')),
                     'user_id': 1, 'category': 'Экологическая'})
print(response.json())

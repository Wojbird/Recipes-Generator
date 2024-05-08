import requests
import json
import random

api_url = "https://app.swaggerhub.com/apis/fdcnal/food-data_central_api/1.0.1#/FDC/getFoods"

query_params = {
    "api_key": "ogX8dMPS4WkeECgx2QItA7ZZPE8yNenBGbGJQmbK", 
    "query": "chicken"
}

response = requests.get(api_url, params=query_params)

if response.status_code == 200:
    data = response.json()
    try:
        with open('data.json', 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    for item in data['foods']:
        existing_data.append({
            'name': item['description'],
            'ingredients': item['foodNutrients'],
            'random_data': random.randint(1, 100) 
        })

    with open('data.json', 'w') as f:
        json.dump(existing_data, f)
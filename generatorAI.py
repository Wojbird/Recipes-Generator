import json
import random
from openai import OpenAI
import requests

with open('ingredients_list.json', 'r', encoding='utf-8') as file:
    grocery_list = json.load(file)

# Funkcja losująca produkty z listy
def draw_products(product_list, num_products):
    if num_products > len(product_list):
        raise ValueError("Ilość produktów do wylosowania przekracza długość listy produktów.")
    return random.sample(product_list, num_products)

# Przykład użycia funkcji
num_products_to_draw = 5
drawn_products = draw_products(grocery_list, num_products_to_draw)

# Wyświetlenie wylosowanych produktów
print(f"Wylosowane produkty ({num_products_to_draw}):")
for item in drawn_products:
    print(item)

# Wstawienie wylosowanych produktów do zapytania
ingredients = ", ".join(drawn_products)
prompt = f"Create a recipe using the given products: {ingredients}. Write only instruction step by step and name of recipe in first line. Dont' write anything else"

# Klucz API i baza URL do OpenAI
openai_api_key = "jUhuG2SrdScI1eXkacuChnpjGSEU2O8wzgQqc3VnXZOAJmFW"
openai_api_base = "https://services.clarin-pl.eu/api/v1/oapi"

# Utworzenie klienta OpenAI
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Wysłanie zapytania do API OpenAI
response = client.chat.completions.create(
  model="openchat",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
  ]
)

# Wyświetlenie odpowiedzi
message = response.choices[0].message.content
print(message)

# Przetworzenie odpowiedzi
lines = message.split("\n")
recipe_name = lines[0]
steps = [line for line in lines[1:] if line.strip() != ""]

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzc1MmIxNWYtZGUxNy00YTE1LWEyM2UtZTBjYmI3YzhlZDg4IiwidHlwZSI6ImFwaV90b2tlbiJ9.43eOlq8Arh765bNIs9r7Otm2cR6AePy4TwCEt4WYE_I",
    "Content-Type": "application/json"
}

url = "https://api.edenai.run/v2/image/generation"
payload = {
    "providers": ['openai/dall-e-2'],
    "text": recipe_name,
    "resolution": "256x256",
    "fallback_providers": []
}

response = requests.post(url, json=payload, headers=headers)
result = json.loads(response.text)

if 'openai/dall-e-2' in result and 'items' in result['openai/dall-e-2']:
    image_url = result['openai/dall-e-2']['items'][0]['image_resource_url']
    print(image_url)
else:
    image_url = None
    print("Image generation failed or no image URL found.")

# Zapisanie przepisu w liście słowników
recipe = {
    "name": recipe_name,
    "steps": steps,
    "image_url": image_url
}

# Przykład zapisu wielu przepisów do listy
recipes = []
recipes.append(recipe)

# Wyświetlenie zapisanego przepisu
print("\nSaved recipe:")
print(f"Name: {recipe['name']}")
for step in recipe['steps']:
    print(step)
if recipe['image_url']:
    print(f"Image URL: {recipe['image_url']}")
else:
    print("No image available.")
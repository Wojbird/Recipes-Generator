import json
import random
from openai import OpenAI
import requests


def generate_recipes(ingredients_list, num_iterations, client, headers):
    recipes = []
    for _ in range(num_iterations):
        # Losowanie produktów z listy składników
        drawn_products = random.sample(ingredients_list, 5)

        # Wstawienie wylosowanych produktów do zapytania
        ingredients = ", ".join(drawn_products)
        prompt = f"Create a recipe using the given products: {ingredients}. Write only instruction step by step and name of recipe in first line. Dont' write anything else"

        # Wysłanie zapytania do API OpenAI
        response = client.chat.completions.create(
            model="openchat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        # Przetworzenie odpowiedzi
        message = response.choices[0].message.content
        lines = message.split("\n")
        recipe_name = lines[0]
        steps = [line for line in lines[1:] if line.strip() != ""]

        # Generowanie obrazka (zakomentowane)
        # url = "https://api.edenai.run/v2/image/generation"
        # payload = {
        #     "providers": ['openai/dall-e-2'],
        #     "text": recipe_name,
        #     "resolution": "256x256",
        #     "fallback_providers": []
        # }
        # response = requests.post(url, json=payload, headers=headers)
        # result = json.loads(response.text)
        # if 'openai/dall-e-2' in result and 'items' in result['openai/dall-e-2']:
        #     image_url = result['openai/dall-e-2']['items'][0]['image_resource_url']
        # else:
        #     image_url = None

        # Zapisanie przepisu w liście słowników
        recipe = {
            "name": recipe_name,
            "steps": steps,
            "image_url": None,  # Wstawiamy null jako adres URL obrazka
            "ingredients": drawn_products
        }
        recipes.append(recipe)
    return recipes


def display_recipes(recipes):
    for recipe in recipes:
        print("\nSaved recipe:")
        print(f"Name: {recipe['name']}")
        print(f"Ingredients: {', '.join(recipe['ingredients'])}")
        for step in recipe['steps']:
            print(step)
        if recipe['image_url']:
            print(f"Image URL: {recipe['image_url']}")
        else:
            print("No image available.")
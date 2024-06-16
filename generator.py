import random
import json
# takie cos bo mi sie cos jebało i to pomogło
# sys.path.insert(0, 'C:\\Users\\Wiktoria\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python312\\site-packages')
# sys.path.insert(0, 'C:\\Users\\wojma\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\fatsecret')
from fatsecret import Fatsecret
from openai import OpenAI
from openai.resources.beta.threads.runs import steps

import generatorAI

#klucze do generator AI potrzebne do działania funkcji generatorAI.generate_recipes-----------------------------------------------------------
# Klucz API i baza URL do OpenAI
openai_api_key = "jUhuG2SrdScI1eXkacuChnpjGSEU2O8wzgQqc3VnXZOAJmFW"
openai_api_base = "https://services.clarin-pl.eu/api/v1/oapi"

# Utworzenie klienta OpenAI
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzc1MmIxNWYtZGUxNy00YTE1LWEyM2UtZTBjYmI3YzhlZDg4IiwidHlwZSI6ImFwaV90b2tlbiJ9.43eOlq8Arh765bNIs9r7Otm2cR6AePy4TwCEt4WYE_I",
    "Content-Type": "application/json"
}
#----------------------------------------------------------------------------------------------------

#wczytywanie pliku konfiguracyjnego
config = open('dbconfig.json')
configData = json.load(config)

recipes_counter = int(configData["Recipes create number"])
ingredients_counter = int(configData["Ingredients create number"])
other_tables_counter = int(configData["Other tables create number"])

#recipes_counter = configData["Recipes create number"]
#ingredients_counter = configData["Ingredients create number"]


consumer_key = '53c67ce11c5443218bb25a81c64931ad'
consumer_secret = '609224f5084243ab83e92876a927c87c'

# Create a Fatsecret session
fs = Fatsecret(consumer_key, consumer_secret)


# Funkcja do generowania losowych ID składników
def generate_random_food_ids(num_ids):
    food_ids = set()
    while len(food_ids) < num_ids:
        food_ids.add(random.randint(1, 300000))  # Zakres ID dostępny w API FatSecret
    return list(food_ids)


# Wygenerowanie 100 losowych ID składników
num_ingredients = ingredients_counter
random_food_ids = generate_random_food_ids(num_ingredients)

# Lista na informacje o składnikach
ingredients_data = []

# Pobieranie informacji o każdym składniku
for food_id in random_food_ids:
    try:
        food_details = fs.food_get(food_id)

        # Zbieranie informacji do listy
        ingredient_info = {
            "Name": food_details['food_name'],
            "Description": food_details.get('food_description', 'No description available.'),
            "Serving Size": food_details.get('serving_description', 'No serving size information available.'),
            "Calories": food_details.get('calories', random.randint(50, 300)),
            "Protein": food_details.get('protein', round(random.uniform(1, 20), 2)),
            "Carbohydrates": food_details.get('carbohydrate', round(random.uniform(1, 50), 2)),
            "Fat": food_details.get('fat', round(random.uniform(1, 30), 2))
        }

        ingredients_data.append(ingredient_info)

        # Wyświetlenie informacji
        print("\nAll information:")
        print(f"Name: {ingredient_info['Name']}")
        print(f"Description: {ingredient_info['Description']}")
        print(f"Serving Size: {ingredient_info['Serving Size']}")
        print(f"Calories: {ingredient_info['Calories']} kcal")
        print(f"Protein: {ingredient_info['Protein']} g")
        print(f"Carbohydrates: {ingredient_info['Carbohydrates']} g")
        print(f"Fat: {ingredient_info['Fat']} g")

    except Exception as e:
        print(f"Error fetching information for food_id {food_id}: {str(e)}")

# Zapis do pliku data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(ingredients_data, f, ensure_ascii=False, indent=4)

# Zapis listy składników do ingredients_list.json
ingredient_names = [ingredient_info['Name'] for ingredient_info in ingredients_data]
with open('ingredients_list.json', 'w', encoding='utf-8') as f:
    json.dump(ingredient_names, f, ensure_ascii=False, indent=4)

#generator AI
recipes = generatorAI.generate_recipes(ingredient_names, ingredients_counter, client, headers)
generatorAI.display_recipes(recipes)
#-----------------------------------------------


#-------------------------------------------------------------------------------------------------------------------

#kopiowanie txt
source_sql = open('input.txt', 'r')
destination_sql = open('output.txt', 'w')

for line in source_sql:
    destination_sql.write(line)

source_sql.close()

#AI gen

# recipes_counter = range(recipes_counter)
# ingredients_counter = range(ingredients_counter)
# other_tables_counter = range(other_tables_counter)
steps_counter = range(1)
counter = range(1)

#-----------------------------------------------------------------------------------------------------------------------

database = {
    "Tables":
        [
            {
                "Table name": tab["Table name"],
                "Columns":
                    [
                        {
                            "Column name": col["Field name"],
                            "Data list":
                                [
                                    {
                                        "List":
                                        {
                                            "List":
                                            {
                                                "Data": recipes[recipe]["name"],
                                            } if (col["Field name"] == "Name") else
                                            {
                                                {
                                                    {
                                                        {
                                                            "Data": 0,  #pierwsza wartość PK, dodać pozostałe warunki
                                                        } if recipe - 1 == 0 else
                                                        {
                                                            "Data": database[tab["Table name"]][col["Field name"]][recipes[recipe]["name"]][recipe - 1] + 1,
                                                            #inkrementacja, dodać pozostałe warunki
                                                        }
                                                    } if "integer" in col["Type"] else
                                                    {
                                                        {
                                                            "Data": "a",  #pierwsza wartość PK, dodać pozostałe warunki
                                                        } if recipe - 1 == 0 else
                                                        {
                                                            "Data": chr(ord(database[tab["Table name"]][col["Field name"]][recipes[recipe]["name"]][recipe - 1]) + 1),
                                                            #inkrementacja, dodać pozostałe warunki
                                                        }
                                                    } if "char" in col["Type"][
                                                        "Type"] else "" and print("Wrong PK datatype!") and quit()
                                                }
                                            } if (col["Unique"] == "true") else
                                            {
                                                "Data": "NULL",
                                                #dorobić sprawdzanie i uzupełnianie (może w nowym loopie)!!!
                                            } if (col["FK References"] != "null") else
                                            {
                                                {
                                                    "Data": col["Default"],
                                                } if (col["Default"] != "null") else
                                                {
                                                    "Data": "NULL",
                                                } if (col["Nullable"] != "null") else
                                                {
                                                    {
                                                        "Data": random.choice(string.ascii_letters)
                                                    } if "char" in col["Type"] else
                                                    {
                                                        "Data": random.choice(string.ascii_letters)
                                                    } if "varchar" in col["Type"] else
                                                    {
                                                        "Data": "00:00:00",
                                                    } if "time" in col["Type"] else
                                                    {
                                                        "Data": random.randint(0, 1000),
                                                    } if "integer" in col["Type"] else
                                                    {
                                                        "Data": random.uniform(0, 1000),
                                                    } if "float" in col["Type"] else
                                                    {
                                                        "Data": random.uniform(0, 1000), #sprawdzić czy nie ma dla double?
                                                    } if "double" in col["Type"] else
                                                    {
                                                        "Data": decimal.Decimal(random.randint(0, 1000)/pow(10, random.randint(0, 3))),
                                                    } if "decimal" in col["Type"] else
                                                    {
                                                        "Data": "",
                                                    }
                                                }
                                            }
                                        } for recipe in range(recipes_counter)
                                    } if (tab["Table name"] == "Recipes") else ""
                                    # {
                                    #     {
                                    #         {
                                    #             #----------
                                    #         } if (col["Field name"] == "Name") else ""
                                    #     } for recipe in ingredients_counter
                                    # } if (tab["Table name"] == "Ingredients") else
                                    # {
                                    #     {
                                    #         {
                                    #             #----------
                                    #         } if (col["Field name"] == "Name") else ""
                                    #     } for recipe in steps_counter
                                    # } if (tab["Table name"] == "Steps") else
                                    # {
                                    #     {
                                    #         {
                                    #             #----------
                                    #         } if (col["Field name"] == "Name") else ""
                                    #     } for recipe in recipes_counter
                                    # } if (tab["Table name"] == "Ingredients_Steps") else
                                    # {
                                    #     {
                                    #         {
                                    #             {
                                    #                 "Data": col["Default"],
                                    #             } if (col["Default"] != "null") else
                                    #             {
                                    #                 "Data": "NULL",
                                    #             } if (col["Nullable"] != "null") else
                                    #             {
                                    #                 #----------
                                    #             }
                                    #         } if (col["Field name"] == "Name") else ""
                                    #     } for recipe in counter
                                    # }
                                ]
                        } for col in tab["Fields"]
                    ]
            } for tab in configData["Tables"]
        ]
}

for tab in database["Tables"]:
    for col in tab["Columns"]:
        for data in col["Data list"]:
            print(data_str["List"]["List"]["Data"])
            destination_sql.write(
                "\nINSERT INTO " + tab["Table name"] + "(" + col["Column name"] + ") VALUES(" +
                "data" + ");"
            )

config.close()
destination_sql.close()

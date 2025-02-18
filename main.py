import pandas as pd
import random
from datetime import datetime

def load_disliked_ingredients(filename):
    df = pd.read_excel(filename, sheet_name="Marco's dislikes")
    return set(df["ingredient"])

def load_ingredients(filename):
    df = pd.read_excel(filename, sheet_name="Ingredients")
    return dict(zip(df["ingredient"], df["cost"]))

def load_recipes(filename, ingredients):
    df = pd.read_excel(filename, sheet_name="Recipes")
    recipes = []
    for _, row in df.iterrows():
        ingredient_list = set(row["ingredients"].split(", "))
        cost = sum(ingredients.get(ing, 0) for ing in ingredient_list)
        recipes.append({
            "name": row["name"],
            "ingredients": ingredient_list,
            "cost": cost,
            "time": int(row["time"])
        })
    return recipes

def filter_recipes(recipes, disliked_ingredients, time_limit=None):
    valid_recipes = [
        recipe for recipe in recipes
        if not disliked_ingredients.intersection(recipe["ingredients"])
        and (time_limit is None or recipe["time"] <= time_limit)
    ]
    return valid_recipes

def suggest_dinner(recipes, disliked_ingredients, time_limit=None):
    valid_recipes = filter_recipes(recipes, disliked_ingredients, time_limit)
    if not valid_recipes:
        return "No suitable recipes found. Consider ordering takeout!"
    return random.choice(valid_recipes)["name"]

def log_dinner_choice(filename, recipe_name):
    location = input("Where did you eat (home/restaurant/etc.)? ")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = pd.DataFrame([[date, recipe_name, location]], columns=["date", "recipe", "location"])
    
    try:
        history_df = pd.read_excel(filename, sheet_name="Archive")
        history_df = pd.concat([history_df, log_entry], ignore_index=True)
    except FileNotFoundError:
        history_df = log_entry
    
    with pd.ExcelWriter(filename, mode="a", if_sheet_exists="replace") as writer:
        history_df.to_excel(writer, sheet_name="Archive", index=False)

# Main:
disliked_ingredients = load_disliked_ingredients("recipes_data.xlsx")
ingredients = load_ingredients("recipes_data.xlsx")
recipes = load_recipes("recipes_data.xlsx", ingredients)
time_available = 20  # Adjust this based on when they get home
chosen_recipe = suggest_dinner(recipes, disliked_ingredients, time_available)
print("Suggested dinner:", chosen_recipe)
log_dinner_choice("recipes_data.xlsx", chosen_recipe)

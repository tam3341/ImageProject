import requests

class MealDBAPI:
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    @staticmethod
    def search_by_name(meal_name):
        url = f"{MealDBAPI.BASE_URL}/search.php?s={meal_name}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('meals')
        return None

    @staticmethod
    def search_by_ingredient(ingredient):
        formatted_ingredient = ingredient.replace(" ", "_")
        url = f"{MealDBAPI.BASE_URL}/filter.php?i={formatted_ingredient}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('meals')
        return None

    @staticmethod
    def get_meal_details(meal_id):
        url = f"{MealDBAPI.BASE_URL}/lookup.php?i={meal_id}"
        response = requests.get(url)
        if response.status_code == 200:
            meals = response.json().get('meals')
            if meals:
                return meals[0]
        return None

    @staticmethod
    def get_recipe_ingredients(meal_data):
        ingredients = []
        for i in range(1, 21):
            ingredient = meal_data.get(f'strIngredient{i}')
            if ingredient and ingredient.strip():
                ingredients.append(ingredient.strip().lower())
        return ingredients

    @staticmethod
    def search_by_multiple_ingredients(pantry_ingredients):
        if not pantry_ingredients:
            return []

        pantry_ingredients = [ing.lower() for ing in pantry_ingredients]

        primary_ingredient = pantry_ingredients[0]
        base_meals = MealDBAPI.search_by_ingredient(primary_ingredient)

        if not base_meals:
            return []

        recommended_recipes = []

        for meal in base_meals[:5]:
            meal_id = meal['idMeal']
            meal_details = MealDBAPI.get_meal_details(meal_id)

            if not meal_details:
                continue

            recipe_ingredients = MealDBAPI.get_recipe_ingredients(meal_details)

            matches = [ing for ing in recipe_ingredients if any(pantry_ing in ing for pantry_ing in pantry_ingredients)]
            missing = [ing for ing in recipe_ingredients if
                       not any(pantry_ing in ing for pantry_ing in pantry_ingredients)]

            match_percentage = (len(matches) / len(recipe_ingredients)) * 100 if recipe_ingredients else 0

            recommended_recipes.append({
                "name": meal_details['strMeal'],
                "match_percentage": round(match_percentage, 1),
                "missing_ingredients": missing,
                "thumbnail": meal_details['strMealThumb'],
                "instructions": meal_details['strInstructions']
            })

        return sorted(recommended_recipes, key=lambda x: x['match_percentage'], reverse=True)
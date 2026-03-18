from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
import os

from schemas import GroceryItem, Ingredient, MacroTargets, Meal

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

STANDARD_TEMPLATES = {
    "breakfast": [
        {
            "name": "Protein Oat Bowl",
            "prep_minutes": 8,
            "protein_g": 32,
            "carbs_g": 46,
            "fat_g": 11,
            "calories": 405,
            "ingredients": [
                {"name": "rolled oats", "amount": 70, "unit": "g", "category": "carbs"},
                {
                    "name": "greek yogurt",
                    "amount": 180,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "banana", "amount": 120, "unit": "g", "category": "produce"},
                {"name": "chia seeds", "amount": 10, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Egg and Toast Plate",
            "prep_minutes": 10,
            "protein_g": 30,
            "carbs_g": 34,
            "fat_g": 15,
            "calories": 395,
            "ingredients": [
                {"name": "eggs", "amount": 180, "unit": "g", "category": "protein"},
                {
                    "name": "sourdough bread",
                    "amount": 90,
                    "unit": "g",
                    "category": "carbs",
                },
                {"name": "spinach", "amount": 60, "unit": "g", "category": "produce"},
                {"name": "berries", "amount": 80, "unit": "g", "category": "produce"},
            ],
        },
    ],
    "lunch": [
        {
            "name": "Chicken Rice Bowl",
            "prep_minutes": 18,
            "protein_g": 42,
            "carbs_g": 58,
            "fat_g": 12,
            "calories": 520,
            "ingredients": [
                {
                    "name": "chicken breast",
                    "amount": 170,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "brown rice", "amount": 180, "unit": "g", "category": "carbs"},
                {"name": "broccoli", "amount": 120, "unit": "g", "category": "produce"},
                {"name": "olive oil", "amount": 8, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Turkey Sweet Potato Plate",
            "prep_minutes": 18,
            "protein_g": 40,
            "carbs_g": 54,
            "fat_g": 11,
            "calories": 495,
            "ingredients": [
                {
                    "name": "ground turkey",
                    "amount": 165,
                    "unit": "g",
                    "category": "protein",
                },
                {
                    "name": "sweet potato",
                    "amount": 220,
                    "unit": "g",
                    "category": "carbs",
                },
                {
                    "name": "green beans",
                    "amount": 120,
                    "unit": "g",
                    "category": "produce",
                },
                {"name": "olive oil", "amount": 7, "unit": "g", "category": "pantry"},
            ],
        },
    ],
    "snack": [
        {
            "name": "Yogurt Crunch Cup",
            "prep_minutes": 5,
            "protein_g": 24,
            "carbs_g": 28,
            "fat_g": 9,
            "calories": 285,
            "ingredients": [
                {
                    "name": "greek yogurt",
                    "amount": 180,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "granola", "amount": 35, "unit": "g", "category": "carbs"},
                {
                    "name": "blueberries",
                    "amount": 80,
                    "unit": "g",
                    "category": "produce",
                },
                {"name": "almonds", "amount": 15, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Protein Smoothie",
            "prep_minutes": 5,
            "protein_g": 26,
            "carbs_g": 24,
            "fat_g": 7,
            "calories": 255,
            "ingredients": [
                {"name": "milk", "amount": 250, "unit": "ml", "category": "dairy"},
                {"name": "banana", "amount": 100, "unit": "g", "category": "produce"},
                {
                    "name": "peanut butter",
                    "amount": 12,
                    "unit": "g",
                    "category": "pantry",
                },
                {
                    "name": "whey powder",
                    "amount": 30,
                    "unit": "g",
                    "category": "protein",
                },
            ],
        },
    ],
    "dinner": [
        {
            "name": "Salmon Potato Plate",
            "prep_minutes": 20,
            "protein_g": 38,
            "carbs_g": 46,
            "fat_g": 17,
            "calories": 505,
            "ingredients": [
                {"name": "salmon", "amount": 160, "unit": "g", "category": "protein"},
                {"name": "potatoes", "amount": 240, "unit": "g", "category": "carbs"},
                {"name": "salad mix", "amount": 90, "unit": "g", "category": "produce"},
                {"name": "olive oil", "amount": 9, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Beef Quinoa Bowl",
            "prep_minutes": 18,
            "protein_g": 39,
            "carbs_g": 44,
            "fat_g": 15,
            "calories": 495,
            "ingredients": [
                {
                    "name": "lean beef",
                    "amount": 150,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "quinoa", "amount": 170, "unit": "g", "category": "carbs"},
                {
                    "name": "bell peppers",
                    "amount": 100,
                    "unit": "g",
                    "category": "produce",
                },
                {"name": "zucchini", "amount": 100, "unit": "g", "category": "produce"},
            ],
        },
    ],
    "evening": [
        {
            "name": "Cottage Cheese Berry Bowl",
            "prep_minutes": 4,
            "protein_g": 24,
            "carbs_g": 18,
            "fat_g": 6,
            "calories": 210,
            "ingredients": [
                {
                    "name": "cottage cheese",
                    "amount": 200,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "berries", "amount": 80, "unit": "g", "category": "produce"},
                {"name": "honey", "amount": 10, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Turkey Wrap",
            "prep_minutes": 7,
            "protein_g": 22,
            "carbs_g": 24,
            "fat_g": 7,
            "calories": 235,
            "ingredients": [
                {
                    "name": "turkey slices",
                    "amount": 100,
                    "unit": "g",
                    "category": "protein",
                },
                {
                    "name": "whole wheat tortilla",
                    "amount": 60,
                    "unit": "g",
                    "category": "carbs",
                },
                {"name": "lettuce", "amount": 40, "unit": "g", "category": "produce"},
                {"name": "tomato", "amount": 60, "unit": "g", "category": "produce"},
            ],
        },
    ],
}

VEGETARIAN_TEMPLATES = {
    "breakfast": [
        {
            "name": "Tofu Scramble Toast",
            "prep_minutes": 10,
            "protein_g": 28,
            "carbs_g": 34,
            "fat_g": 12,
            "calories": 360,
            "ingredients": [
                {
                    "name": "firm tofu",
                    "amount": 180,
                    "unit": "g",
                    "category": "protein",
                },
                {
                    "name": "sourdough bread",
                    "amount": 90,
                    "unit": "g",
                    "category": "carbs",
                },
                {"name": "spinach", "amount": 60, "unit": "g", "category": "produce"},
                {"name": "olive oil", "amount": 7, "unit": "g", "category": "pantry"},
            ],
        },
        {
            "name": "Overnight Protein Oats",
            "prep_minutes": 6,
            "protein_g": 26,
            "carbs_g": 42,
            "fat_g": 9,
            "calories": 345,
            "ingredients": [
                {"name": "rolled oats", "amount": 65, "unit": "g", "category": "carbs"},
                {
                    "name": "greek yogurt",
                    "amount": 180,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "berries", "amount": 90, "unit": "g", "category": "produce"},
                {"name": "chia seeds", "amount": 10, "unit": "g", "category": "pantry"},
            ],
        },
    ],
    "lunch": [
        {
            "name": "Tofu Rice Bowl",
            "prep_minutes": 18,
            "protein_g": 35,
            "carbs_g": 58,
            "fat_g": 12,
            "calories": 470,
            "ingredients": [
                {
                    "name": "firm tofu",
                    "amount": 220,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "brown rice", "amount": 180, "unit": "g", "category": "carbs"},
                {"name": "broccoli", "amount": 120, "unit": "g", "category": "produce"},
                {"name": "sesame oil", "amount": 8, "unit": "g", "category": "pantry"},
            ],
        }
    ],
    "snack": [
        {
            "name": "Protein Yogurt Cup",
            "prep_minutes": 4,
            "protein_g": 24,
            "carbs_g": 26,
            "fat_g": 8,
            "calories": 270,
            "ingredients": [
                {
                    "name": "greek yogurt",
                    "amount": 200,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "berries", "amount": 80, "unit": "g", "category": "produce"},
                {"name": "granola", "amount": 35, "unit": "g", "category": "carbs"},
            ],
        }
    ],
    "dinner": [
        {
            "name": "Lentil Quinoa Bowl",
            "prep_minutes": 20,
            "protein_g": 33,
            "carbs_g": 52,
            "fat_g": 10,
            "calories": 430,
            "ingredients": [
                {"name": "lentils", "amount": 200, "unit": "g", "category": "protein"},
                {"name": "quinoa", "amount": 170, "unit": "g", "category": "carbs"},
                {
                    "name": "roasted vegetables",
                    "amount": 140,
                    "unit": "g",
                    "category": "produce",
                },
                {"name": "olive oil", "amount": 8, "unit": "g", "category": "pantry"},
            ],
        }
    ],
    "evening": [
        {
            "name": "Cottage Cheese Fruit Cup",
            "prep_minutes": 4,
            "protein_g": 22,
            "carbs_g": 18,
            "fat_g": 5,
            "calories": 190,
            "ingredients": [
                {
                    "name": "cottage cheese",
                    "amount": 180,
                    "unit": "g",
                    "category": "protein",
                },
                {"name": "apple", "amount": 100, "unit": "g", "category": "produce"},
                {"name": "cinnamon", "amount": 2, "unit": "g", "category": "pantry"},
            ],
        }
    ],
}

MEAL_SLOTS = {
    4: ["breakfast", "lunch", "snack", "dinner"],
    5: ["breakfast", "lunch", "snack", "dinner", "evening"],
}

MEAL_RATIOS = {
    4: [0.24, 0.30, 0.16, 0.30],
    5: [0.22, 0.25, 0.14, 0.24, 0.15],
}


def calculate_macros(weight: float, unit: str, goal: str) -> MacroTargets:
    pounds = weight * 2.20462 if unit == "kg" else weight
    calorie_factor = {
        "cut": 14.0,
        "maintain": 15.5,
        "bulk": 17.0,
    }.get(goal, 15.5)
    calories = round(pounds * calorie_factor)
    protein_g = round(pounds * 1.0)
    fat_g = max(45, round(pounds * 0.4))
    carbs_g = max(120, round((calories - protein_g * 4 - fat_g * 9) / 4))
    return MacroTargets(
        calories=calories, protein_g=protein_g, carbs_g=carbs_g, fat_g=fat_g
    )


def _filtered_options(slot: str, restrictions: list[str]) -> list[dict]:
    vegetarian = "vegetarian" in restrictions
    dairy_free = "dairy-free" in restrictions
    nut_free = "nut-free" in restrictions

    source = VEGETARIAN_TEMPLATES if vegetarian else STANDARD_TEMPLATES
    options = deepcopy(source[slot])

    if dairy_free:
        options = [
            option
            for option in options
            if all(
                item["name"]
                not in {"greek yogurt", "milk", "whey powder", "cottage cheese"}
                for item in option["ingredients"]
            )
        ] or options
    if nut_free:
        options = [
            option
            for option in options
            if all(
                item["name"] not in {"almonds", "peanut butter"}
                for item in option["ingredients"]
            )
        ] or options
    return options


def _scale_meal(slot: str, template: dict, ratio: float, macros: MacroTargets) -> Meal:
    target_calories = max(180, round(macros.calories * ratio))
    factor = target_calories / template["calories"]
    ingredients = [
        Ingredient(
            name=item["name"],
            amount=max(1, round(item["amount"] * factor)),
            unit=item["unit"],
            category=item["category"],
        )
        for item in template["ingredients"]
    ]
    return Meal(
        slot=slot,
        name=template["name"],
        prep_minutes=template["prep_minutes"],
        protein_g=max(1, round(template["protein_g"] * factor)),
        carbs_g=max(1, round(template["carbs_g"] * factor)),
        fat_g=max(1, round(template["fat_g"] * factor)),
        calories=target_calories,
        ingredients=ingredients,
    )


def build_meal_plan(
    macros: MacroTargets,
    meal_count: int,
    restrictions: list[str],
    variant_seed: int = 0,
) -> list[Meal]:
    slots = MEAL_SLOTS[meal_count]
    ratios = MEAL_RATIOS[meal_count]
    meals: list[Meal] = []
    for index, slot in enumerate(slots):
        options = _filtered_options(slot, restrictions)
        choice = options[(variant_seed + index) % len(options)]
        meals.append(_scale_meal(slot, choice, ratios[index], macros))
    return meals


def _try_llm_plan(
    macros: MacroTargets, meal_count: int, restrictions: list[str]
) -> list[Meal] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        return None

    slots = MEAL_SLOTS[meal_count]
    model = os.getenv("NUTRIPLAN_LLM_MODEL", "gpt-5.4")
    client = OpenAI(api_key=api_key, timeout=20.0)
    prompt = {
        "meal_count": meal_count,
        "slots": slots,
        "calories": macros.calories,
        "protein_g": macros.protein_g,
        "carbs_g": macros.carbs_g,
        "fat_g": macros.fat_g,
        "dietary_restrictions": restrictions,
    }
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.5,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sports nutrition planner. Return strict JSON with a top-level 'meals' array. "
                        "Each meal must include name, prep_minutes, protein_g, carbs_g, fat_g, calories, and ingredients. "
                        "Each ingredient must include name, amount, unit, and category. Keep prep under 20 minutes."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt),
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        meals_data = payload.get("meals", [])
        if len(meals_data) != meal_count:
            return None

        meals: list[Meal] = []
        for slot, item in zip(slots, meals_data, strict=True):
            ingredients = [
                Ingredient(
                    name=str(ingredient.get("name", "ingredient")).strip()
                    or "ingredient",
                    amount=max(1, int(round(float(ingredient.get("amount", 1))))),
                    unit=str(ingredient.get("unit", "g")).strip() or "g",
                    category=str(ingredient.get("category", "pantry")).strip()
                    or "pantry",
                )
                for ingredient in item.get("ingredients", [])
                if isinstance(ingredient, dict)
            ]
            if not ingredients:
                return None
            meals.append(
                Meal(
                    slot=slot,
                    name=str(item.get("name", slot.title())).strip() or slot.title(),
                    prep_minutes=min(20, max(3, int(item.get("prep_minutes", 10)))),
                    protein_g=max(1, int(item.get("protein_g", 1))),
                    carbs_g=max(1, int(item.get("carbs_g", 1))),
                    fat_g=max(1, int(item.get("fat_g", 1))),
                    calories=max(120, int(item.get("calories", 120))),
                    ingredients=ingredients,
                )
            )
        return meals
    except Exception:
        return None


def build_meal_plan_with_mode(
    macros: MacroTargets,
    meal_count: int,
    restrictions: list[str],
    variant_seed: int = 0,
) -> tuple[list[Meal], str]:
    llm_meals = _try_llm_plan(macros, meal_count, restrictions)
    if llm_meals is not None:
        return llm_meals, "llm"
    return build_meal_plan(
        macros, meal_count, restrictions, variant_seed
    ), "deterministic"


def swap_meal(
    current_meals: list[dict],
    meal_index: int,
    macros: MacroTargets,
    restrictions: list[str],
) -> list[Meal]:
    meal_count = len(current_meals)
    slots = MEAL_SLOTS[meal_count]
    slot = slots[meal_index]
    ratios = MEAL_RATIOS[meal_count]
    options = _filtered_options(slot, restrictions)
    current_name = current_meals[meal_index]["name"]
    choice_index = 0
    for idx, option in enumerate(options):
        if option["name"] == current_name:
            choice_index = (idx + 1) % len(options)
            break
    replacement = _scale_meal(slot, options[choice_index], ratios[meal_index], macros)
    meals = [Meal.model_validate(item) for item in current_meals]
    meals[meal_index] = replacement
    return meals


def build_grocery_list(meals: list[dict]) -> list[GroceryItem]:
    totals: dict[tuple[str, str, str], int] = defaultdict(int)
    for meal in meals:
        for ingredient in meal["ingredients"]:
            key = (ingredient["name"], ingredient["unit"], ingredient["category"])
            totals[key] += int(ingredient["amount"])
    items = [
        GroceryItem(name=name, unit=unit, category=category, amount=amount)
        for (name, unit, category), amount in totals.items()
    ]
    return sorted(items, key=lambda item: (item.category, item.name))

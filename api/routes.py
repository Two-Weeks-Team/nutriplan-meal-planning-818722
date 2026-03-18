import json
import random
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_service import call_inference
from models import NPMeal, NPMealPlan, NPUserProfile, SessionLocal, parse_json_list


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PlanRequest(BaseModel):
    query: str
    preferences: str = ""


class InsightsRequest(BaseModel):
    selection: str
    context: str = ""


class MacroRequest(BaseModel):
    name: str = "Athlete"
    weight_lb: float
    goal: str
    activity: str = "moderate"
    diet_style: str = "balanced"
    exclusions: list[str] = Field(default_factory=list)


class SwapRequest(BaseModel):
    plan_id: int
    meal_id: int
    lock_meal_ids: list[int] = Field(default_factory=list)
    preferences: str = ""


def _macro_targets(weight_lb: float, goal: str, activity: str):
    goal = goal.lower().strip()
    activity = activity.lower().strip()

    base = weight_lb * 14
    if goal in ["cut", "cutting", "fat loss"]:
        base -= 300
    elif goal in ["gain", "muscle gain", "bulk", "lean bulk"]:
        base += 300

    activity_mod = {
        "low": -120,
        "moderate": 0,
        "high": 180,
    }.get(activity, 0)

    calories = int(max(1600, base + activity_mod))
    protein = int(round(weight_lb * (1.0 if goal in ["maintenance", "maintain"] else 1.1)))
    fat = int(round((calories * 0.27) / 9))
    carbs = int(round((calories - (protein * 4 + fat * 9)) / 4))

    return calories, protein, carbs, fat


def _calc_kcal(p, c, f):
    return int(p * 4 + c * 4 + f * 9)


@router.get("/demo")
@router.get("/demo")
def get_demo(db: Session = Depends(get_db)):
    latest = db.query(NPMealPlan).order_by(NPMealPlan.created_at.desc()).first()
    if not latest:
        return {"summary": "No plans yet", "items": [], "score": 0}

    meals = db.query(NPMeal).filter(NPMeal.plan_id == latest.id).all()
    items = []
    for m in meals:
        items.append({
            "meal_id": m.id,
            "slot": m.slot,
            "name": m.name,
            "portion_badge": m.portion_label,
            "prep_minutes": m.prep_minutes,
            "protein_g": m.protein_g,
            "carbs_g": m.carbs_g,
            "fat_g": m.fat_g,
            "calories": m.calories,
            "macro_contribution_pct": {
                "protein": round((m.protein_g / max(1, latest.protein_target)) * 100, 1),
                "carbs": round((m.carbs_g / max(1, latest.carbs_target)) * 100, 1),
                "fat": round((m.fat_g / max(1, latest.fat_target)) * 100, 1),
            },
            "ingredients": parse_json_list(m.ingredients_json),
            "aisles": parse_json_list(m.aisle_tags_json),
            "locked": m.locked,
        })

    actual_p = sum(x["protein_g"] for x in items)
    actual_c = sum(x["carbs_g"] for x in items)
    actual_f = sum(x["fat_g"] for x in items)
    score = max(0, 100 - abs(actual_p - latest.protein_target) - abs(actual_c - latest.carbs_target) * 0.3 - abs(actual_f - latest.fat_target) * 0.8)

    return {
        "summary": latest.title,
        "items": items,
        "score": round(score, 1),
        "target": {
            "calories": latest.calories_target,
            "protein_g": latest.protein_target,
            "carbs_g": latest.carbs_target,
            "fat_g": latest.fat_target,
        },
        "grocery": parse_json_list(latest.grocery_json),
        "notes": latest.notes,
    }


@router.post("/macro-target")
@router.post("/macro-target")
def macro_target(payload: MacroRequest):
    calories, protein, carbs, fat = _macro_targets(payload.weight_lb, payload.goal, payload.activity)
    breakdown = [
        f"Base calories = weight({payload.weight_lb}) * 14",
        f"Goal adjustment applied for {payload.goal}",
        f"Activity adjustment applied for {payload.activity}",
        f"Protein anchored near {round(payload.weight_lb * 1.1)}g for performance",
    ]
    return {
        "daily_macro_target": {
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
        },
        "breakdown": breakdown,
        "profile": payload.model_dump(),
    }


@router.post("/plan")
@router.post("/plan")
async def create_plan(payload: PlanRequest, db: Session = Depends(get_db)):
    q = payload.query.lower()
    weight = 180.0
    goal = "cutting"
    name = "Alex"
    if "maya" in q:
        name, weight, goal = "Maya", 135.0, "muscle gain"
    elif "jordan" in q:
        name, weight, goal = "Jordan", 205.0, "maintenance"

    calories, protein, carbs, fat = _macro_targets(weight, goal, "moderate")

    prompt = {
        "task": "Generate exactly 5 meals with macros that approximately match target totals.",
        "target": {"calories": calories, "protein_g": protein, "carbs_g": carbs, "fat_g": fat},
        "preferences": payload.preferences,
        "output_schema": {
            "summary": "string",
            "meals": [
                {
                    "slot": "breakfast|snack|lunch|pre-workout|dinner",
                    "name": "string",
                    "portion_label": "string",
                    "prep_minutes": 12,
                    "protein_g": 30,
                    "carbs_g": 40,
                    "fat_g": 12,
                    "ingredients": ["item"],
                    "aisles": ["produce|protein|grain|dairy|pantry|frozen"]
                }
            ],
            "rationale_notes": ["string"],
            "grocery_by_aisle": [{"aisle": "produce", "items": ["spinach - 200g"]}]
        }
    }

    ai = await call_inference([
        {"role": "system", "content": "You are a sports nutrition meal planner. Return strict JSON object only."},
        {"role": "user", "content": json.dumps(prompt)},
    ])

    meals = ai.get("meals") if isinstance(ai, dict) else None
    if not isinstance(meals, list) or len(meals) < 4:
        meals = [
            {"slot": "breakfast", "name": "Greek Yogurt Oats Bowl", "portion_label": "1 bowl", "prep_minutes": 8, "protein_g": 40, "carbs_g": 55, "fat_g": 12, "ingredients": ["greek yogurt", "oats", "berries", "chia"], "aisles": ["dairy", "grain", "produce"]},
            {"slot": "snack", "name": "Whey Banana Shake", "portion_label": "1 shaker", "prep_minutes": 4, "protein_g": 30, "carbs_g": 32, "fat_g": 4, "ingredients": ["whey", "banana", "milk"], "aisles": ["protein", "produce", "dairy"]},
            {"slot": "lunch", "name": "Chicken Rice Bowl", "portion_label": "1 plate", "prep_minutes": 18, "protein_g": 48, "carbs_g": 70, "fat_g": 14, "ingredients": ["chicken breast", "jasmine rice", "broccoli", "olive oil"], "aisles": ["protein", "grain", "produce", "pantry"]},
            {"slot": "pre-workout", "name": "Turkey Wrap", "portion_label": "1 wrap", "prep_minutes": 10, "protein_g": 35, "carbs_g": 42, "fat_g": 10, "ingredients": ["turkey", "whole wheat wrap", "lettuce", "hummus"], "aisles": ["protein", "grain", "produce", "pantry"]},
            {"slot": "dinner", "name": "Salmon Sweet Potato Plate", "portion_label": "1 plate", "prep_minutes": 22, "protein_g": 42, "carbs_g": 58, "fat_g": 20, "ingredients": ["salmon", "sweet potato", "asparagus"], "aisles": ["protein", "produce"]},
        ]

    user = NPUserProfile(name=name, weight_lb=weight, goal=goal, activity="moderate", diet_style="balanced", exclusions_json="[]")
    db.add(user)
    db.flush()

    plan = NPMealPlan(
        user_id=user.id,
        title=f"{name} {goal.title()} Meal Day",
        goal=goal,
        calories_target=calories,
        protein_target=protein,
        carbs_target=carbs,
        fat_target=fat,
        notes="; ".join(ai.get("rationale_notes", ["Macro-balanced day generated with fallback-safe planner."])),
        grocery_json=json.dumps(ai.get("grocery_by_aisle", [])),
    )
    db.add(plan)
    db.flush()

    items = []
    for meal in meals[:5]:
        p = int(meal.get("protein_g", 0))
        c = int(meal.get("carbs_g", 0))
        f = int(meal.get("fat_g", 0))
        rec = NPMeal(
            plan_id=plan.id,
            slot=str(meal.get("slot", "meal")),
            name=str(meal.get("name", "Meal")),
            ingredients_json=json.dumps(meal.get("ingredients", [])),
            aisle_tags_json=json.dumps(meal.get("aisles", [])),
            prep_minutes=int(meal.get("prep_minutes", 12)),
            portion_label=str(meal.get("portion_label", "1 serving")),
            protein_g=p,
            carbs_g=c,
            fat_g=f,
            calories=_calc_kcal(p, c, f),
            locked=False,
        )
        db.add(rec)
        db.flush()
        items.append({
            "meal_id": rec.id,
            "slot": rec.slot,
            "name": rec.name,
            "portion_badge": rec.portion_label,
            "prep_minutes": rec.prep_minutes,
            "protein_g": rec.protein_g,
            "carbs_g": rec.carbs_g,
            "fat_g": rec.fat_g,
            "calories": rec.calories,
            "ingredients": parse_json_list(rec.ingredients_json),
            "aisles": parse_json_list(rec.aisle_tags_json),
            "locked": rec.locked,
        })

    db.commit()

    total_p = sum(i["protein_g"] for i in items)
    total_c = sum(i["carbs_g"] for i in items)
    total_f = sum(i["fat_g"] for i in items)
    score = max(0, 100 - abs(total_p - protein) - abs(total_c - carbs) * 0.3 - abs(total_f - fat) * 0.8)

    return {
        "summary": ai.get("summary", f"Generated 5-meal day for {name}"),
        "items": items,
        "score": round(score, 1),
        "plan_id": plan.id,
        "target": {"calories": calories, "protein_g": protein, "carbs_g": carbs, "fat_g": fat},
        "grocery": parse_json_list(plan.grocery_json),
        "note": ai.get("note", "generated_with_ai_or_fallback"),
    }


@router.post("/insights")
@router.post("/insights")
async def plan_insights(payload: InsightsRequest):
    prompt = {
        "task": "Analyze selected meal plan and return coaching insights.",
        "selection": payload.selection,
        "context": payload.context,
        "output_schema": {
            "insights": ["string"],
            "next_actions": ["string"],
            "highlights": ["string"]
        }
    }
    ai = await call_inference([
        {"role": "system", "content": "You are a practical macro coach. Return strict JSON object only."},
        {"role": "user", "content": json.dumps(prompt)},
    ])

    return {
        "insights": ai.get("insights", ["Protein pacing across the day is balanced for recovery."]),
        "next_actions": ai.get("next_actions", ["Lock your favorite lunch, then swap dinner for variety."]),
        "highlights": ai.get("highlights", ["Grocery list ready and grouped by aisle."]),
        "note": ai.get("note", "generated_with_ai_or_fallback"),
    }

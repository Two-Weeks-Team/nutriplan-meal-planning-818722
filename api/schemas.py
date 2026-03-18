from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlannerInput(BaseModel):
    weight: float = Field(gt=30, lt=250)
    unit: str = Field(default="kg")
    goal: str = Field(default="maintain")
    meal_count: int = Field(default=4, ge=4, le=5)
    dietary_restrictions: list[str] = Field(default_factory=list)


class MacroTargets(BaseModel):
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int


class Ingredient(BaseModel):
    name: str
    amount: int
    unit: str
    category: str


class Meal(BaseModel):
    slot: str
    name: str
    prep_minutes: int
    protein_g: int
    carbs_g: int
    fat_g: int
    calories: int
    ingredients: list[Ingredient]


class MealPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    weight: float
    unit: str
    goal: str
    dietary_restrictions: list[str]
    meal_count: int
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    generator_mode: str
    meals: list[Meal]
    is_saved: bool


class PlanListResponse(BaseModel):
    plans: list[MealPlanResponse]


class GroceryItem(BaseModel):
    name: str
    amount: int
    unit: str
    category: str


class GroceryListResponse(BaseModel):
    plan_id: str
    items: list[GroceryItem]


class SavePlanResponse(BaseModel):
    id: str
    is_saved: bool

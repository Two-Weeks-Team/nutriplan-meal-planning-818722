from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db, get_engine, init_db
from models import MealPlan
from planner import (
    build_grocery_list,
    build_meal_plan_with_mode,
    calculate_macros,
    swap_meal,
)
from schemas import (
    GroceryListResponse,
    MacroTargets,
    MealPlanResponse,
    PlanListResponse,
    PlannerInput,
    SavePlanResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="NutriPlan API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)


def to_plan_response(plan: MealPlan) -> MealPlanResponse:
    return MealPlanResponse(
        id=plan.id,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        weight=plan.weight,
        unit=plan.unit,
        goal=plan.goal,
        dietary_restrictions=plan.dietary_restrictions,
        meal_count=plan.meal_count,
        calories=plan.calories,
        protein_g=plan.protein_g,
        carbs_g=plan.carbs_g,
        fat_g=plan.fat_g,
        generator_mode=plan.generator_mode,
        meals=plan.meals,
        is_saved=plan.is_saved,
    )


@app.get("/health")
def health() -> dict[str, str]:
    with Session(get_engine()) as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/api/calculate", response_model=MacroTargets)
def calculate(payload: PlannerInput) -> MacroTargets:
    return calculate_macros(payload.weight, payload.unit, payload.goal)


@app.post("/api/generate-plan", response_model=MealPlanResponse)
def generate_plan(
    payload: PlannerInput, db: Session = Depends(get_db)
) -> MealPlanResponse:
    macros = calculate_macros(payload.weight, payload.unit, payload.goal)
    meals, generator_mode = build_meal_plan_with_mode(
        macros, payload.meal_count, payload.dietary_restrictions
    )
    plan = MealPlan(
        weight=payload.weight,
        unit=payload.unit,
        goal=payload.goal,
        dietary_restrictions=payload.dietary_restrictions,
        meal_count=payload.meal_count,
        calories=macros.calories,
        protein_g=macros.protein_g,
        carbs_g=macros.carbs_g,
        fat_g=macros.fat_g,
        generator_mode=generator_mode,
        meals=[meal.model_dump() for meal in meals],
        is_saved=False,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return to_plan_response(plan)


@app.get("/api/plans", response_model=PlanListResponse)
def list_plans(db: Session = Depends(get_db)) -> PlanListResponse:
    plans = db.query(MealPlan).order_by(MealPlan.created_at.desc()).all()
    return PlanListResponse(plans=[to_plan_response(plan) for plan in plans])


@app.get("/api/plans/{plan_id}", response_model=MealPlanResponse)
def get_plan(plan_id: str, db: Session = Depends(get_db)) -> MealPlanResponse:
    plan = db.get(MealPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return to_plan_response(plan)


@app.patch("/api/plans/{plan_id}/meals/{meal_index}", response_model=MealPlanResponse)
def replace_meal(
    plan_id: str, meal_index: int, db: Session = Depends(get_db)
) -> MealPlanResponse:
    plan = db.get(MealPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if meal_index < 0 or meal_index >= len(plan.meals):
        raise HTTPException(status_code=400, detail="Meal index out of range")
    macros = MacroTargets(
        calories=plan.calories,
        protein_g=plan.protein_g,
        carbs_g=plan.carbs_g,
        fat_g=plan.fat_g,
    )
    meals = swap_meal(plan.meals, meal_index, macros, plan.dietary_restrictions)
    plan.meals = [meal.model_dump() for meal in meals]
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return to_plan_response(plan)


@app.post("/api/plans/{plan_id}/save", response_model=SavePlanResponse)
def save_plan(plan_id: str, db: Session = Depends(get_db)) -> SavePlanResponse:
    plan = db.get(MealPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.is_saved = True
    db.add(plan)
    db.commit()
    return SavePlanResponse(id=plan.id, is_saved=True)


@app.get("/api/grocery-list/{plan_id}", response_model=GroceryListResponse)
def grocery_list(plan_id: str, db: Session = Depends(get_db)) -> GroceryListResponse:
    plan = db.get(MealPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return GroceryListResponse(plan_id=plan_id, items=build_grocery_list(plan.meals))

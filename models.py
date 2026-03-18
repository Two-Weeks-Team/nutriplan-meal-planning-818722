import json
import os
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


raw_database_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_database_url.startswith("postgresql+asyncpg://"):
    raw_database_url = raw_database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif raw_database_url.startswith("postgres://"):
    raw_database_url = raw_database_url.replace("postgres://", "postgresql+psycopg://", 1)

is_sqlite = raw_database_url.startswith("sqlite")
is_local = "localhost" in raw_database_url or "127.0.0.1" in raw_database_url

engine_kwargs = {"future": True}
if not is_sqlite and not is_local:
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(raw_database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class NPUserProfile(Base):
    __tablename__ = "np_user_profiles"

    id = Integer().with_variant(Integer, "sqlite")
    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    name = __import__("sqlalchemy").Column(String(120), nullable=False)
    weight_lb = __import__("sqlalchemy").Column(Float, nullable=False)
    goal = __import__("sqlalchemy").Column(String(50), nullable=False)
    activity = __import__("sqlalchemy").Column(String(50), nullable=False, default="moderate")
    diet_style = __import__("sqlalchemy").Column(String(50), nullable=False, default="balanced")
    exclusions_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    plans = relationship("NPMealPlan", back_populates="user", cascade="all, delete-orphan")


class NPMealPlan(Base):
    __tablename__ = "np_meal_plans"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    user_id = __import__("sqlalchemy").Column(Integer, ForeignKey("np_user_profiles.id"), nullable=False, index=True)
    title = __import__("sqlalchemy").Column(String(180), nullable=False)
    goal = __import__("sqlalchemy").Column(String(50), nullable=False)
    calories_target = __import__("sqlalchemy").Column(Integer, nullable=False)
    protein_target = __import__("sqlalchemy").Column(Integer, nullable=False)
    carbs_target = __import__("sqlalchemy").Column(Integer, nullable=False)
    fat_target = __import__("sqlalchemy").Column(Integer, nullable=False)
    notes = __import__("sqlalchemy").Column(Text, nullable=False, default="")
    grocery_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    is_favorite = __import__("sqlalchemy").Column(Boolean, nullable=False, default=False)
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("NPUserProfile", back_populates="plans")
    meals = relationship("NPMeal", back_populates="plan", cascade="all, delete-orphan")


class NPMeal(Base):
    __tablename__ = "np_meals"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    plan_id = __import__("sqlalchemy").Column(Integer, ForeignKey("np_meal_plans.id"), nullable=False, index=True)
    slot = __import__("sqlalchemy").Column(String(40), nullable=False)
    name = __import__("sqlalchemy").Column(String(180), nullable=False)
    ingredients_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    aisle_tags_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    prep_minutes = __import__("sqlalchemy").Column(Integer, nullable=False, default=10)
    portion_label = __import__("sqlalchemy").Column(String(60), nullable=False, default="1 serving")
    protein_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=0)
    carbs_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=0)
    fat_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=0)
    calories = __import__("sqlalchemy").Column(Integer, nullable=False, default=0)
    locked = __import__("sqlalchemy").Column(Boolean, nullable=False, default=False)

    plan = relationship("NPMealPlan", back_populates="meals")


def parse_json_list(text_value: str):
    try:
        value = json.loads(text_value or "[]")
        if isinstance(value, list):
            return value
        return []
    except Exception:
        return []

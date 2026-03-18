from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    weight: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(8))
    goal: Mapped[str] = mapped_column(String(16))
    dietary_restrictions: Mapped[list[str]] = mapped_column(JSON, default=list)
    meal_count: Mapped[int] = mapped_column(Integer)
    calories: Mapped[int] = mapped_column(Integer)
    protein_g: Mapped[int] = mapped_column(Integer)
    carbs_g: Mapped[int] = mapped_column(Integer)
    fat_g: Mapped[int] = mapped_column(Integer)
    generator_mode: Mapped[str] = mapped_column(String(16), default="deterministic")
    meals: Mapped[list[dict]] = mapped_column(JSON, default=list)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

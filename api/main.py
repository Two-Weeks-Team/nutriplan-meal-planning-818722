from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from models import Base, NPMeal, NPMealPlan, NPUserProfile, SessionLocal, engine
from routes import router


app = FastAPI(title="Nutriplan Meal Planning API", version="1.0.0")

Base.metadata.create_all(bind=engine)


def seed_data():
    db = SessionLocal()
    try:
        existing = db.query(NPMealPlan).first()
        if existing:
            return

        seeds = [
            ("Alex", 180.0, "cutting", 2200, 200, 220, 65, "High-protein chicken rice bowl day plan"),
            ("Maya", 135.0, "muscle gain", 2400, 150, 300, 70, "Vegetarian lean bulk meal set"),
            ("Jordan", 205.0, "maintenance", 2600, 210, 290, 80, "Balanced maintenance athlete plate"),
        ]

        for name, weight, goal, kcal, p, c, f, title in seeds:
            user = NPUserProfile(name=name, weight_lb=weight, goal=goal, activity="moderate", diet_style="balanced", exclusions_json="[]")
            db.add(user)
            db.flush()

            plan = NPMealPlan(
                user_id=user.id,
                title=title,
                goal=goal,
                calories_target=kcal,
                protein_target=p,
                carbs_target=c,
                fat_target=f,
                notes="Seeded demo plan for instant first-load proof.",
                grocery_json='[{"aisle":"produce","items":["spinach - 200g","banana - 4"]}]',
            )
            db.add(plan)
            db.flush()

            db.add(NPMeal(plan_id=plan.id, slot="breakfast", name="Protein Oats", ingredients_json='["oats","whey","berries"]', aisle_tags_json='["grain","protein","produce"]', prep_minutes=8, portion_label="1 bowl", protein_g=35, carbs_g=55, fat_g=10, calories=450, locked=False))
            db.add(NPMeal(plan_id=plan.id, slot="lunch", name="Chicken Rice Bowl", ingredients_json='["chicken","rice","broccoli"]', aisle_tags_json='["protein","grain","produce"]', prep_minutes=18, portion_label="1 plate", protein_g=50, carbs_g=70, fat_g=15, calories=615, locked=True))
            db.add(NPMeal(plan_id=plan.id, slot="dinner", name="Salmon Potato Plate", ingredients_json='["salmon","potato","greens"]', aisle_tags_json='["protein","produce"]', prep_minutes=22, portion_label="1 plate", protein_g=45, carbs_g=60, fat_g=20, calories=600, locked=False))

        db.commit()
    finally:
        db.close()


seed_data()

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <html>
      <head>
        <title>Nutriplan Meal Planning API</title>
        <style>
          body { background:#0f1115; color:#e7f7ee; font-family:Arial, sans-serif; margin:0; padding:24px; }
          .card { background:#171b22; border:1px solid #26303d; border-radius:12px; padding:16px; margin-bottom:14px; }
          h1 { color:#7CFF9E; margin-bottom:6px; }
          a { color:#7CFF9E; text-decoration:none; }
          code { color:#b6ffd0; }
          .muted { color:#9fb3a8; }
        </style>
      </head>
      <body>
        <h1>Nutriplan Meal Planning</h1>
        <p class='muted'>From body stats to a macro-balanced meal day in one click.</p>

        <div class='card'>
          <h3>Tech Stack</h3>
          <p>FastAPI 0.115.0 · SQLAlchemy 2.0.35 · Pydantic 2.9.0 · httpx 0.27.0 · PostgreSQL-ready models · DO Serverless Inference</p>
        </div>

        <div class='card'>
          <h3>Endpoints</h3>
          <ul>
            <li><code>GET /health</code></li>
            <li><code>GET /demo</code> (also <code>/api/demo</code>)</li>
            <li><code>POST /macro-target</code> (also <code>/api/macro-target</code>)</li>
            <li><code>POST /plan</code> (also <code>/api/plan</code>)</li>
            <li><code>POST /insights</code> (also <code>/api/insights</code>)</li>
          </ul>
        </div>

        <div class='card'>
          <h3>Docs</h3>
          <p><a href='/docs'>/docs</a> · <a href='/redoc'>/redoc</a></p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

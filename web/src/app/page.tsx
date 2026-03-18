"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  calculate,
  generatePlan,
  getGroceryList,
  getPlan,
  listPlans,
  savePlan,
  swapMeal,
  type GroceryItem,
  type MacroTargets,
  type MealPlan,
  type PlannerInput,
} from "@/lib/api";

const DEFAULT_INPUT: PlannerInput = {
  weight: 75,
  unit: "kg",
  goal: "maintain",
  meal_count: 4,
  dietary_restrictions: [],
};

const RESTRICTIONS = ["vegetarian", "dairy-free", "nut-free"];

export default function Page() {
  const [form, setForm] = useState<PlannerInput>(DEFAULT_INPUT);
  const [macroTargets, setMacroTargets] = useState<MacroTargets | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<MealPlan | null>(null);
  const [plans, setPlans] = useState<MealPlan[]>([]);
  const [groceryItems, setGroceryItems] = useState<GroceryItem[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshPlans = useCallback(async (selectedId?: string) => {
    const payload = await listPlans();
    setPlans(payload.plans);
    const activeId = selectedId || selectedPlan?.id || payload.plans[0]?.id;
    if (activeId) {
      const plan = await getPlan(activeId);
      const grocery = await getGroceryList(activeId);
      setSelectedPlan(plan);
      setGroceryItems(grocery.items);
    }
  }, [selectedPlan?.id]);

  useEffect(() => {
    refreshPlans().catch(() => {
      setPlans([]);
    });
  }, [refreshPlans]);

  const generationLabel = useMemo(() => {
    if (!selectedPlan) {
      return "No plan generated yet";
    }
    return selectedPlan.generator_mode === "llm" ? "AI-enhanced generation" : "Deterministic planner";
  }, [selectedPlan]);

  async function handleCalculate() {
    setBusy("calculate");
    setError(null);
    try {
      setMacroTargets(await calculate(form));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to calculate macros.");
    } finally {
      setBusy(null);
    }
  }

  async function handleGenerate() {
    setBusy("generate");
    setError(null);
    try {
      const plan = await generatePlan(form);
      setSelectedPlan(plan);
      setMacroTargets({
        calories: plan.calories,
        protein_g: plan.protein_g,
        carbs_g: plan.carbs_g,
        fat_g: plan.fat_g,
      });
      const grocery = await getGroceryList(plan.id);
      setGroceryItems(grocery.items);
      await refreshPlans(plan.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate meal plan.");
    } finally {
      setBusy(null);
    }
  }

  async function handleSwap(mealIndex: number) {
    if (!selectedPlan) return;
    setBusy(`swap-${mealIndex}`);
    setError(null);
    try {
      const updated = await swapMeal(selectedPlan.id, mealIndex);
      setSelectedPlan(updated);
      const grocery = await getGroceryList(updated.id);
      setGroceryItems(grocery.items);
      await refreshPlans(updated.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to swap meal.");
    } finally {
      setBusy(null);
    }
  }

  async function handleSave() {
    if (!selectedPlan) return;
    setBusy("save");
    setError(null);
    try {
      await savePlan(selectedPlan.id);
      await refreshPlans(selectedPlan.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save plan.");
    } finally {
      setBusy(null);
    }
  }

  function toggleRestriction(value: string) {
    setForm((current) => ({
      ...current,
      dietary_restrictions: current.dietary_restrictions.includes(value)
        ? current.dietary_restrictions.filter((item) => item !== value)
        : [...current.dietary_restrictions, value],
    }));
  }

  return (
    <main className="page">
      <div className="shell">
        <section className="hero">
          <span className="eyebrow">NutriPlan MVP</span>
          <h1>Tell NutriPlan your weight and goal. It plans the day, totals the groceries, and lets you swap meals live.</h1>
          <p>
            This standalone app is designed for reliable local operation: FastAPI, Next.js, PostgreSQL, and Docker. If an
            OpenAI key is available through the sibling `../vibeDeploy/agent/.env`, the backend attempts GPT-5.4 generation first and
            returns to the deterministic planner automatically when that path fails.
          </p>
        </section>

        <section className="layout">
          <aside className="panel">
            <div className="panel-inner">
              <h2 className="panel-title">Planner input</h2>
              <p className="panel-copy">Keep the MVP tight: pick a goal, set meal count, then generate a meal plan that is easy to cook and easy to repeat.</p>
              <div className="form-grid">
                <div className="inline-grid">
                  <div className="field">
                    <label htmlFor="weight">Weight</label>
                    <input
                      id="weight"
                      type="number"
                      value={form.weight}
                      min={30}
                      max={250}
                      onChange={(event) => setForm((current) => ({ ...current, weight: Number(event.target.value) }))}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="unit">Unit</label>
                    <select
                      id="unit"
                      value={form.unit}
                      onChange={(event) => setForm((current) => ({ ...current, unit: event.target.value as PlannerInput["unit"] }))}
                    >
                      <option value="kg">kg</option>
                      <option value="lb">lb</option>
                    </select>
                  </div>
                </div>

                <div className="inline-grid">
                  <div className="field">
                    <label htmlFor="goal">Goal</label>
                    <select
                      id="goal"
                      value={form.goal}
                      onChange={(event) => setForm((current) => ({ ...current, goal: event.target.value as PlannerInput["goal"] }))}
                    >
                      <option value="cut">Cut</option>
                      <option value="maintain">Maintain</option>
                      <option value="bulk">Bulk</option>
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor="meal-count">Meals per day</label>
                    <select
                      id="meal-count"
                      value={form.meal_count}
                      onChange={(event) => setForm((current) => ({ ...current, meal_count: Number(event.target.value) as 4 | 5 }))}
                    >
                      <option value={4}>4 meals</option>
                      <option value={5}>5 meals</option>
                    </select>
                  </div>
                </div>

                <div className="field">
                  <p style={{ margin: 0, fontWeight: 700, fontSize: "0.92rem" }}>Dietary restrictions</p>
                  <div className="restriction-grid">
                    {RESTRICTIONS.map((restriction) => (
                      <button
                        key={restriction}
                        type="button"
                        className={`chip ${form.dietary_restrictions.includes(restriction) ? "active" : ""}`}
                        onClick={() => toggleRestriction(restriction)}
                      >
                        {restriction}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="action-row">
                  <button type="button" className="button secondary" onClick={handleCalculate} disabled={busy !== null}>
                    {busy === "calculate" ? "Calculating..." : "Calculate macros"}
                  </button>
                  <button type="button" className="button primary" onClick={handleGenerate} disabled={busy !== null}>
                    {busy === "generate" ? "Generating..." : "Generate plan"}
                  </button>
                </div>

                <div className="status-row">
                  <span className="badge">Backend-first flow</span>
                  <span className={`badge ${selectedPlan?.generator_mode === "llm" ? "ai" : ""}`}>{generationLabel}</span>
                </div>

                {error ? <p className="error">{error}</p> : null}
              </div>
            </div>
          </aside>

          <section className="stack">
            <div className="panel">
              <div className="panel-inner">
                <h2 className="panel-title">Daily targets</h2>
                <p className="panel-copy">The planner uses weight-based calorie math and then spreads the total across 4 or 5 meals.</p>
                <div className="metrics">
                  {[
                    ["Calories", macroTargets?.calories ?? selectedPlan?.calories ?? 0],
                    ["Protein", macroTargets?.protein_g ?? selectedPlan?.protein_g ?? 0],
                    ["Carbs", macroTargets?.carbs_g ?? selectedPlan?.carbs_g ?? 0],
                    ["Fat", macroTargets?.fat_g ?? selectedPlan?.fat_g ?? 0],
                  ].map(([label, value]) => (
                    <div className="metric" key={label}>
                      <div className="metric-label">{label}</div>
                      <div className="metric-value">{value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="content-grid">
              <div className="panel">
                <div className="panel-inner">
                  <h2 className="panel-title">Meal plan</h2>
                  <p className="panel-copy">Every meal includes macros, prep time, ingredients, and a one-click swap action.</p>
                  {selectedPlan ? (
                    <>
                      <div className="action-row" style={{ marginBottom: 18 }}>
                        <button type="button" className="button primary" onClick={handleSave} disabled={busy !== null || selectedPlan.is_saved}>
                          {selectedPlan.is_saved ? "Saved" : busy === "save" ? "Saving..." : "Save favorite"}
                        </button>
                        <span className={`badge ${selectedPlan.generator_mode === "llm" ? "ai" : ""}`}>{selectedPlan.generator_mode}</span>
                      </div>
                      <div className="meal-grid">
                        {selectedPlan.meals.map((meal, index) => (
                          <article className="meal-card" key={`${meal.slot}-${meal.name}`}>
                            <h3>{meal.name}</h3>
                            <div className="meal-meta">
                              <span>{meal.slot}</span>
                              <span>{meal.calories} kcal</span>
                              <span>{meal.prep_minutes} min</span>
                            </div>
                            <div className="meal-meta">
                              <span>P {meal.protein_g}g</span>
                              <span>C {meal.carbs_g}g</span>
                              <span>F {meal.fat_g}g</span>
                            </div>
                            <div className="ingredient-list">
                              {meal.ingredients.map((ingredient) => (
                                <div className="ingredient-row" key={`${meal.name}-${ingredient.name}`}>
                                  <span>{ingredient.name}</span>
                                  <span className="muted">{ingredient.amount}{ingredient.unit}</span>
                                </div>
                              ))}
                            </div>
                            <div className="action-row" style={{ marginTop: 16 }}>
                              <button type="button" className="button ghost" onClick={() => handleSwap(index)} disabled={busy !== null}>
                                {busy === `swap-${index}` ? "Swapping..." : "Swap meal"}
                              </button>
                            </div>
                          </article>
                        ))}
                      </div>
                    </>
                  ) : (
                    <p className="muted">Generate a plan to see the full meal dashboard.</p>
                  )}
                </div>
              </div>

              <div className="stack">
                <div className="panel">
                  <div className="panel-inner">
                    <h2 className="panel-title">Grocery list</h2>
                    <p className="panel-copy">The API aggregates ingredients across the whole day into a single shopping list.</p>
                    {groceryItems.length > 0 ? (
                      <div className="grocery-list">
                        {groceryItems.map((item) => (
                          <div className="grocery-row" key={`${item.category}-${item.name}`}>
                            <div>
                              <strong>{item.name}</strong>
                              <div className="muted">{item.category}</div>
                            </div>
                            <span className="muted">{item.amount}{item.unit}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="muted">Generate a plan to build the grocery list.</p>
                    )}
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-inner">
                    <h2 className="panel-title">Recent plans</h2>
                    <p className="panel-copy">Plans are stored in PostgreSQL so the app survives restarts.</p>
                    <div className="history-list">
                      {plans.length > 0 ? (
                        plans.map((plan) => (
                          <div className="history-row" key={plan.id}>
                            <div>
                              <strong>{plan.goal}</strong>
                              <div className="muted">{plan.calories} kcal · {plan.meal_count} meals · {plan.generator_mode}</div>
                            </div>
                            <button type="button" className="button ghost" onClick={() => refreshPlans(plan.id)} disabled={busy !== null}>
                              Open
                            </button>
                          </div>
                        ))
                      ) : (
                        <p className="muted">No plans yet.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

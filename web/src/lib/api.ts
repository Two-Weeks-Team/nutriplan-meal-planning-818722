const API_BASE = "";

export type PlannerInput = {
  weight: number;
  unit: "kg" | "lb";
  goal: "cut" | "maintain" | "bulk";
  meal_count: 4 | 5;
  dietary_restrictions: string[];
};

export type MacroTargets = {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
};

export type Ingredient = {
  name: string;
  amount: number;
  unit: string;
  category: string;
};

export type Meal = {
  slot: string;
  name: string;
  prep_minutes: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  calories: number;
  ingredients: Ingredient[];
};

export type MealPlan = PlannerInput & {
  id: string;
  created_at: string;
  updated_at: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  generator_mode: string;
  meals: Meal[];
  is_saved: boolean;
};

export type GroceryItem = {
  name: string;
  amount: number;
  unit: string;
  category: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function calculate(payload: PlannerInput) {
  return request<MacroTargets>("/api/calculate", { method: "POST", body: JSON.stringify(payload) });
}
export function generatePlan(payload: PlannerInput) {
  return request<MealPlan>("/api/generate-plan", { method: "POST", body: JSON.stringify(payload) });
}
export function listPlans() {
  return request<{ plans: MealPlan[] }>("/api/plans");
}
export function getPlan(planId: string) {
  return request<MealPlan>(`/api/plans/${planId}`);
}
export function swapMeal(planId: string, mealIndex: number) {
  return request<MealPlan>(`/api/plans/${planId}/meals/${mealIndex}`, { method: "PATCH" });
}
export function savePlan(planId: string) {
  return request<{ id: string; is_saved: boolean }>(`/api/plans/${planId}/save`, { method: "POST" });
}
export function getGroceryList(planId: string) {
  return request<{ plan_id: string; items: GroceryItem[] }>(`/api/grocery-list/${planId}`);
}

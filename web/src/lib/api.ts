export type PlanRequest = {
  query: string;
  preferences: string;
};

export async function generatePlan(payload: PlanRequest) {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Could not generate meal day.");
  return res.json();
}

export async function fetchInsights(selection: string, context: string) {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection, context })
  });
  if (!res.ok) throw new Error("Could not load insights.");
  return res.json();
}

"use client";

import { useState } from "react";
import { generatePlan } from "@/lib/api";
import StatePanel from "@/components/StatePanel";

export default function WorkspacePanel() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState("Loaded demo seed for Alex Kim · lean bulk · high protein");

  const run = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await generatePlan({
        weight: 82,
        unit: "kg",
        goal: "bulk",
        meal_count: 5,
        dietary_restrictions: []
      });
      setSummary(`${data.meals.length} meals generated for a ${data.goal} plan`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="flex items-center justify-between">
        <h2 className="font-[--font-display] text-2xl">Meal Plan Studio</h2>
        <button
          type="button"
          onClick={run}
          className="rounded-md bg-primary px-4 py-2 font-medium text-primary-foreground transition hover:opacity-90"
        >
          Generate Meal Plan
        </button>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">{summary}</p>
      <StatePanel loading={loading} error={error} success={!loading && !error} />
    </section>
  );
}

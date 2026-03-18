"use client";

export default function InsightPanel() {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="font-[--font-display] text-xl">Macro Target Engine</h3>
      <p className="text-sm text-muted-foreground">Protein = 1.0g/lb for lean bulk. Calories adjusted +250 above maintenance. Carbs and fats balanced for training output.</p>
      <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-md border border-border bg-muted p-3">Calories: <strong>2900</strong></div>
        <div className="rounded-md border border-border bg-muted p-3">Protein: <strong>180g</strong></div>
        <div className="rounded-md border border-border bg-muted p-3">Carbs: <strong>320g</strong></div>
        <div className="rounded-md border border-border bg-muted p-3">Fats: <strong>85g</strong></div>
      </div>
    </section>
  );
}

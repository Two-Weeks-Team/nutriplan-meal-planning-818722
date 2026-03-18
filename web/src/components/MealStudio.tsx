"use client";

type Props = { refreshKey: number };

export default function MealStudio({ refreshKey }: Props) {
  return (
    <section className="rounded-lg border border-border bg-card/80 p-4 shadow-soft md:p-6" key={refreshKey}>
      <h2 className="text-2xl font-semibold">Meal Day Timeline</h2>
      <p className="mb-4 text-sm text-muted-foreground">Per-meal macro contribution mapped to daily target</p>
      <div className="grid gap-3">
        {["Breakfast", "Snack", "Lunch", "Snack", "Dinner"].map((slot, i) => (
          <article key={`${slot}-${i}`} className="rounded-md border border-border bg-background/50 p-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg">{slot}</h3>
              <span className="text-xs text-success">On Target</span>
            </div>
            <p className="text-sm text-muted-foreground">Plated high-protein dish · 35P / 42C / 12F</p>
          </article>
        ))}
      </div>
    </section>
  );
}

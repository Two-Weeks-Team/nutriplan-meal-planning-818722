"use client";

export default function SideRail() {
  return (
    <aside className="space-y-4">
      <section className="rounded-lg border border-border bg-card/80 p-4 shadow-soft">
        <h3 className="text-xl">Grocery Checklist</h3>
        <ul className="mt-2 space-y-2 text-sm text-muted-foreground">
          <li>Produce · Spinach, bell peppers, bananas</li>
          <li>Protein · Chicken breast, Greek yogurt, eggs</li>
          <li>Pantry · Rice, oats, olive oil</li>
        </ul>
      </section>
      <section className="rounded-lg border border-border bg-card/80 p-4 shadow-soft">
        <h3 className="text-xl">Saved Nutrition Plans</h3>
        <ul className="mt-2 space-y-2 text-sm text-muted-foreground">
          <li>Alex Cutting Day v3</li>
          <li>Vegetarian Lean Bulk Set</li>
          <li>Jordan Maintenance Reset</li>
        </ul>
      </section>
    </aside>
  );
}
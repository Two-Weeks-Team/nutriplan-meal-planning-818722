"use client";

export default function FeaturePanel() {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="font-[--font-display] text-xl">Grocery Receipt + Swap Rebalance</h3>
      <p className="text-sm text-muted-foreground">Swap lunch to turkey wrap and day totals rebalance instantly. Receipt updates without losing checked items.</p>
      <div className="mt-3 rounded-md border border-border bg-muted p-3 text-sm">Aisle Produce: spinach, sweet potatoes, berries • Protein: chicken breast, salmon, greek yogurt</div>
    </section>
  );
}

"use client";

export default function StatsStrip() {
  return (
    <section className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {[
        ["Plans in one pass", "5"],
        ["Target lock confidence", "96%"],
        ["Meals visible", "25"],
        ["Grocery merged lines", "32"]
      ].map(([k, v]) => (
        <div key={k} className="rounded-md border border-border bg-card p-3">
          <p className="text-xs text-muted-foreground">{k}</p>
          <p className="font-[--font-display] text-2xl text-foreground">{v}</p>
        </div>
      ))}
    </section>
  );
}

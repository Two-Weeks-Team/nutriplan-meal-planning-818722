"use client";

export default function ReferenceShelf() {
  return (
    <section className="mt-5 rounded-lg border border-border bg-card p-4">
      <h3 className="font-[--font-display] text-xl">Demo Profiles</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-3 text-sm">
        <div className="rounded-md border border-border bg-muted p-3">Alex Kim · 180 lb · Lean Bulk · High Protein</div>
        <div className="rounded-md border border-border bg-muted p-3">Maya Patel · 135 lb · Fat Loss · Vegetarian</div>
        <div className="rounded-md border border-border bg-muted p-3">Jordan Rivera · 205 lb · Maintenance · Budget-Friendly</div>
      </div>
    </section>
  );
}
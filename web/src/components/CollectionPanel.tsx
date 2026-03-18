"use client";

export default function CollectionPanel() {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="font-[--font-display] text-xl">Saved Plan Shelf</h3>
      <ul className="mt-3 space-y-2 text-sm">
        <li className="rounded-md border border-border bg-muted p-3">Lean Bulk Week A · saved 08:42</li>
        <li className="rounded-md border border-border bg-muted p-3">Vegetarian Fat Loss · saved 07:10</li>
        <li className="rounded-md border border-border bg-muted p-3">Budget Maintenance · saved yesterday</li>
      </ul>
    </section>
  );
}

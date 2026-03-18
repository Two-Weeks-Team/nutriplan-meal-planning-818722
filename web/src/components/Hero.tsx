"use client";

type Props = {
  seeded: string[];
  onGenerate: () => void;
};

export default function Hero({ seeded, onGenerate }: Props) {
  return (
    <header className="rounded-lg border border-border bg-card/80 p-4 shadow-soft md:p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">Nutrition Drafting Table</p>
          <h1 className="text-3xl font-bold leading-tight text-foreground md:text-4xl">Nutriplan Meal Planning</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
            From body stats to a macro-balanced 5-meal day in one click. Lock meals, swap dishes, and keep targets intact.
          </p>
        </div>
        <button
          onClick={onGenerate}
          className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:opacity-90"
        >
          Generate My Meal Day
        </button>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {seeded.map((s) => (
          <span key={s} className="rounded-full border border-border bg-muted px-3 py-1 text-xs text-muted-foreground">
            {s}
          </span>
        ))}
      </div>
    </header>
  );
}

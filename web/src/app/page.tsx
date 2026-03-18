"use client";

import { useMemo, useState } from "react";
import Hero from "@/components/Hero";
import MealStudio from "@/components/MealStudio";
import SideRail from "@/components/SideRail";

export default function Page() {
  const [refreshKey, setRefreshKey] = useState(0);
  const seeded = useMemo(
    () => [
      "Alex — 180 lb, cutting goal, 2200 kcal target",
      "Maya — 135 lb, muscle gain goal, 2400 kcal target",
      "Jordan — 205 lb, maintenance goal, 2600 kcal target"
    ],
    []
  );

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-[1500px] p-4 md:p-6">
        <Hero seeded={seeded} onGenerate={() => setRefreshKey((k) => k + 1)} />
        <section className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-[1.3fr_0.7fr]">
          <MealStudio refreshKey={refreshKey} />
          <SideRail />
        </section>
      </div>
    </main>
  );
}

import type { Metadata } from "next";
import { Rajdhani, Inter } from "next/font/google";
import "@/app/globals.css";

const display = Rajdhani({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700"]
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600"]
});

export const metadata: Metadata = {
  title: "NutriPlan",
  description: "Meal planning with macro targets, grocery lists, and meal swaps."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${display.variable} ${body.variable} bg-background text-foreground antialiased`}>
        {children}
      </body>
    </html>
  );
}

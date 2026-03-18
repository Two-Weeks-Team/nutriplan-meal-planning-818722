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
  title: "Nutriplan Meal Planning",
  description: "From body stats to a macro-balanced meal day in one click."
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

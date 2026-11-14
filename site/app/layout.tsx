import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Hackathons Maroc — veille automatique",
    template: "%s — Hackathons Maroc",
  },
  description:
    "Catalogue à jour des hackathons, datathons et challenges tech au Maroc et en ligne accessibles depuis le Maroc.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen flex flex-col">
        <header className="sticky top-0 z-30 bg-[color:var(--surface)] border-b border-[color:var(--border)]">
          <div className="max-w-6xl mx-auto px-5 py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5 font-semibold">
              <span className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-[color:var(--accent)] text-white font-bold">
                H
              </span>
              <span className="text-base tracking-tight">
                Hackathons Maroc
              </span>
            </Link>
            <nav className="flex items-center gap-5 text-sm text-[color:var(--muted)]">
              <a
                href="https://github.com/niangmamath/hackathon"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[color:var(--foreground)] transition"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="mt-16 border-t border-[color:var(--border)] text-sm text-[color:var(--muted)]">
          <div className="max-w-6xl mx-auto px-5 py-8 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p>
              Veille automatique — scrapers robots.txt-safe, mis à jour tous
              les 2 jours.
            </p>
            <p>Sources : Devpost · MLH · Eventbrite</p>
          </div>
        </footer>
      </body>
    </html>
  );
}

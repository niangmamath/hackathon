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
        <header className="border-b border-[color:var(--border)]">
          <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link href="/" className="font-semibold text-lg">
              Hackathons <span className="text-[color:var(--accent)]">Maroc</span>
            </Link>
            <nav className="text-sm text-[color:var(--muted)]">
              <a
                href="https://github.com/niangmamath/hackathon"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[color:var(--foreground)]"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-[color:var(--border)] text-sm text-[color:var(--muted)]">
          <div className="max-w-6xl mx-auto px-4 py-6">
            Veille automatique — scrapers robots.txt-safe, mis à jour tous les
            2 jours.
          </div>
        </footer>
      </body>
    </html>
  );
}

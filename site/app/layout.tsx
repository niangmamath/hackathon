import type { Metadata } from "next";
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
      <body className="min-h-screen bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}

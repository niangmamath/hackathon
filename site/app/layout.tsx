import type { Metadata } from "next";
import "./globals.css";
import { siteUrl } from "@/lib/site-url";

const title = "Hackathons au Maroc — veille automatique";
const description =
  "Catalogue à jour des hackathons, datathons, ideathons et CTF au Maroc et en ligne accessibles depuis le Maroc. Collecte automatique sur Devpost, MLH et autres plateformes, mise à jour tous les 2 jours.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: title, template: "%s · Hackathons Maroc" },
  description,
  applicationName: "Hackathons Maroc",
  keywords: [
    "hackathon Maroc",
    "hackathon Casablanca",
    "hackathon Rabat",
    "datathon Maroc",
    "ideathon Maroc",
    "challenge tech Maroc",
    "coding competition Maroc",
    "hackathon en ligne",
    "hackathon étudiant Maroc",
    "Devpost",
    "MLH Maroc",
  ],
  authors: [{ name: "Hackathons Maroc" }],
  openGraph: {
    title,
    description,
    url: siteUrl,
    siteName: "Hackathons Maroc",
    locale: "fr_MA",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: { canonical: "/" },
  formatDetection: { email: false, address: false, telephone: false },
  verification: {
    google: "md9SpzEQ7hDP3tyciEux6kK8EpZ2Q_WO7QNa-b_fIRE",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-screen bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}

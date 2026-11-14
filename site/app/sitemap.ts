import type { MetadataRoute } from "next";
import { getHackathons } from "@/lib/db";

const BASE =
  process.env.NEXT_PUBLIC_SITE_URL ||
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "");

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const items = (await getHackathons()) ?? [];
  const now = new Date();
  return [
    { url: `${BASE}/`, lastModified: now, changeFrequency: "daily" },
    ...items.map((h) => ({
      url: `${BASE}/hackathon/${h.slug}`,
      lastModified: new Date(h.derniere_verification),
      changeFrequency: "weekly" as const,
    })),
  ];
}

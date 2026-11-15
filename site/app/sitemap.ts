import type { MetadataRoute } from "next";
import { getHackathons } from "@/lib/db";
import { siteUrl } from "@/lib/site-url";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const items = (await getHackathons()) ?? [];
  const now = new Date();
  return [
    {
      url: `${siteUrl}/`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 1,
    },
    ...items.map((h) => ({
      url: `${siteUrl}/hackathon/${h.slug}`,
      lastModified: new Date(h.derniere_verification),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
  ];
}

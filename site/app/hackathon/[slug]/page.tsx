import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getHackathonBySlug } from "@/lib/db";

export const revalidate = 3600;

type Params = Promise<{ slug: string }>;

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { slug } = await params;
  const h = await getHackathonBySlug(slug);
  if (!h) return { title: "Hackathon introuvable" };
  return {
    title: h.titre,
    description:
      h.description?.slice(0, 160) ||
      `Hackathon ${h.organisateur ?? ""} — ${h.ville ?? "Maroc"}`,
  };
}

export default async function HackathonPage({ params }: { params: Params }) {
  const { slug } = await params;
  const h = await getHackathonBySlug(slug);
  if (!h) notFound();

  // JSON-LD schema.org/Event pour SEO (Google Search Console comprend ce
  // vocabulaire et l'utilise pour les rich results "Event").
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Event",
    name: h.titre,
    description: h.description || undefined,
    url: typeof window === "undefined" ? undefined : window.location.href,
    startDate: h.date_debut || undefined,
    endDate: h.date_fin || undefined,
    eventAttendanceMode: h.en_ligne
      ? "https://schema.org/OnlineEventAttendanceMode"
      : "https://schema.org/OfflineEventAttendanceMode",
    eventStatus: "https://schema.org/EventScheduled",
    organizer: h.organisateur
      ? { "@type": "Organization", name: h.organisateur }
      : undefined,
    location: h.en_ligne
      ? { "@type": "VirtualLocation", url: h.url }
      : {
          "@type": "Place",
          name: h.ville || "Maroc",
          address: { "@type": "PostalAddress", addressCountry: "MA" },
        },
  };

  return (
    <article className="max-w-3xl mx-auto px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav className="mb-6 text-sm">
        <Link
          href="/"
          className="text-[color:var(--muted)] hover:text-[color:var(--foreground)]"
        >
          ← Retour aux hackathons
        </Link>
      </nav>
      <h1 className="text-3xl font-bold tracking-tight mb-3">{h.titre}</h1>
      <div className="flex flex-wrap gap-2 mb-6 text-sm">
        <Badge>{h.fenetre}</Badge>
        {h.domaine && <Badge>{h.domaine}</Badge>}
        {h.en_ligne ? <Badge>En ligne</Badge> : h.ville && <Badge>{h.ville}</Badge>}
        {h.source && (
          <span className="text-[color:var(--muted)] px-2 py-0.5">
            via {h.source}
          </span>
        )}
      </div>

      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm mb-8">
        {h.organisateur && (
          <Row label="Organisateur">{h.organisateur}</Row>
        )}
        {h.date_debut && (
          <Row label="Date de début">{h.date_debut}</Row>
        )}
        {h.date_fin && <Row label="Date de fin">{h.date_fin}</Row>}
        {!h.en_ligne && h.ville && <Row label="Ville">{h.ville}</Row>}
      </dl>

      {h.description && (
        <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap text-[color:var(--foreground)]">
          {h.description}
        </div>
      )}

      {h.url && (
        <div className="mt-8">
          <a
            href={h.url}
            target="_blank"
            rel="noreferrer noopener"
            className="inline-block px-4 py-2 rounded bg-[color:var(--accent)] text-white hover:opacity-90"
          >
            Voir / s&apos;inscrire →
          </a>
        </div>
      )}
    </article>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="px-2 py-0.5 text-xs rounded border border-[color:var(--border)]">
      {children}
    </span>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-[color:var(--muted)]">{label}</dt>
      <dd className="font-medium">{children}</dd>
    </div>
  );
}

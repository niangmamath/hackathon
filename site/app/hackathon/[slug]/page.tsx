import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { getHackathonBySlug } from "@/lib/db";

export const revalidate = 3600;

type Params = Promise<{ slug: string }>;

const FENETRE_STYLE: Record<string, string> = {
  "EN COURS": "bg-emerald-500 text-white",
  IMMINENT: "bg-amber-500 text-white",
  "BIENTÔT": "bg-sky-500 text-white",
  "ANNONCÉ": "bg-slate-500 text-white",
  INCONNUE: "bg-slate-400 text-white",
};

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

  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Event",
    name: h.titre,
    description: h.description || undefined,
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

  const fenStyle = FENETRE_STYLE[h.fenetre] ?? "bg-slate-400 text-white";
  const dates =
    h.date_debut && h.date_fin && h.date_debut !== h.date_fin
      ? `${h.date_debut} → ${h.date_fin}`
      : h.date_debut || h.date_fin || "Date à confirmer";

  return (
    <article className="max-w-3xl mx-auto px-5 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav className="mb-6 text-sm">
        <Link
          href="/"
          className="text-[color:var(--muted)] hover:text-[color:var(--foreground)] transition inline-flex items-center gap-1"
        >
          ← Retour
        </Link>
      </nav>

      <div className="flex items-center gap-2 mb-4">
        <span
          className={`text-xs font-medium px-2.5 py-1 rounded-md ${fenStyle}`}
        >
          {h.fenetre}
        </span>
        {h.en_ligne && (
          <span className="text-xs font-medium px-2.5 py-1 rounded-md border border-[color:var(--border)]">
            En ligne
          </span>
        )}
      </div>

      <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">
        {h.titre}
      </h1>
      {h.organisateur && (
        <p className="text-lg text-[color:var(--muted)] mb-8">
          par {h.organisateur}
        </p>
      )}

      <div className="card p-5 mb-8">
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-sm">
          <Row label="Dates">{dates}</Row>
          <Row label="Lieu">
            {h.en_ligne ? "En ligne — ouvert au Maroc" : h.ville || "Maroc"}
          </Row>
          {h.domaine && <Row label="Domaine">{h.domaine}</Row>}
          {h.source && <Row label="Source">{h.source}</Row>}
        </dl>
      </div>

      {h.description && (
        <div className="whitespace-pre-wrap text-[color:var(--foreground)] leading-relaxed mb-8">
          {h.description}
        </div>
      )}

      {h.url && (
        <a
          href={h.url}
          target="_blank"
          rel="noreferrer noopener"
          className="btn-primary inline-flex items-center gap-2"
        >
          Voir / s&apos;inscrire
          <svg
            className="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M7 17 17 7M7 7h10v10" />
          </svg>
        </a>
      )}
    </article>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-[color:var(--muted)] mb-1">
        {label}
      </dt>
      <dd className="font-medium">{children}</dd>
    </div>
  );
}

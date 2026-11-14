import Link from "next/link";
import type { Hackathon } from "@/lib/db";

const FENETRE_STYLE: Record<string, string> = {
  "EN COURS": "bg-emerald-500 text-white",
  IMMINENT: "bg-amber-500 text-white",
  "BIENTÔT": "bg-sky-500 text-white",
  "ANNONCÉ": "bg-slate-500 text-white",
  INCONNUE: "bg-slate-400 text-white",
};

function formatRange(debut: string | null, fin: string | null) {
  if (!debut && !fin) return "Date à confirmer";
  if (debut && fin && debut !== fin) return `${debut} → ${fin}`;
  return debut || fin || "";
}

export function HackathonCard({ h }: { h: Hackathon }) {
  const fenStyle = FENETRE_STYLE[h.fenetre] ?? "bg-slate-400 text-white";
  return (
    <Link href={`/hackathon/${h.slug}`} className="card p-5 block group">
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="font-semibold leading-snug flex-1 group-hover:text-[color:var(--accent)] transition">
          {h.titre}
        </h3>
        <span
          className={`shrink-0 text-xs font-medium px-2 py-1 rounded-md ${fenStyle}`}
        >
          {h.fenetre}
        </span>
      </div>

      {h.organisateur && (
        <p className="text-sm font-medium mb-2">{h.organisateur}</p>
      )}

      <div className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--muted)] mb-3">
        <span className="inline-flex items-center gap-1">
          {h.en_ligne ? (
            <>
              <IconGlobe />
              En ligne
            </>
          ) : (
            <>
              <IconPin />
              {h.ville || "Maroc"}
            </>
          )}
        </span>
        <span>·</span>
        <span className="inline-flex items-center gap-1">
          <IconCalendar />
          {formatRange(h.date_debut, h.date_fin)}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {h.domaine && (
          <span className="text-xs px-2 py-0.5 rounded-md bg-[color:var(--border)] text-[color:var(--foreground)]">
            {h.domaine}
          </span>
        )}
        {h.source && (
          <span className="text-xs px-2 py-0.5 rounded-md border border-[color:var(--border)] text-[color:var(--muted)]">
            {h.source}
          </span>
        )}
      </div>
    </Link>
  );
}

function IconGlobe() {
  return (
    <svg
      className="w-3.5 h-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}

function IconPin() {
  return (
    <svg
      className="w-3.5 h-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}

function IconCalendar() {
  return (
    <svg
      className="w-3.5 h-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <path d="M16 2v4M8 2v4M3 10h18" />
    </svg>
  );
}

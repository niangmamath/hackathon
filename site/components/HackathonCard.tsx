import Link from "next/link";
import type { Hackathon } from "@/lib/db";

const FENETRE_STYLE: Record<string, string> = {
  "EN COURS": "bg-green-100 text-green-800 border-green-300",
  IMMINENT: "bg-yellow-100 text-yellow-800 border-yellow-300",
  "BIENTÔT": "bg-emerald-100 text-emerald-800 border-emerald-300",
  "ANNONCÉ": "bg-blue-100 text-blue-800 border-blue-300",
  INCONNUE: "bg-gray-100 text-gray-700 border-gray-300",
};

function formatRange(debut: string | null, fin: string | null) {
  if (!debut && !fin) return "Date à confirmer";
  if (debut && fin && debut !== fin) return `${debut} → ${fin}`;
  return debut || fin || "";
}

export function HackathonCard({ h }: { h: Hackathon }) {
  const fenStyle =
    FENETRE_STYLE[h.fenetre] ?? "bg-gray-100 text-gray-700 border-gray-300";
  return (
    <Link
      href={`/hackathon/${h.slug}`}
      className="block rounded-lg border border-[color:var(--border)] p-4 hover:border-[color:var(--accent)] transition"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold leading-snug flex-1">{h.titre}</h3>
        <span
          className={`shrink-0 text-xs px-2 py-0.5 rounded border ${fenStyle}`}
        >
          {h.fenetre}
        </span>
      </div>
      <div className="mt-2 text-sm text-[color:var(--muted)] space-y-0.5">
        {h.organisateur && <div>{h.organisateur}</div>}
        <div>
          {h.en_ligne ? "En ligne" : h.ville || "Maroc"} ·{" "}
          {formatRange(h.date_debut, h.date_fin)}
        </div>
        {h.domaine && (
          <div className="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-[color:var(--border)]/40">
            {h.domaine}
          </div>
        )}
      </div>
    </Link>
  );
}

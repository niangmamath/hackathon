import Link from "next/link";
import type { Hackathon } from "@/lib/db";
import {
  ArrowRightIcon,
  CalendarIcon,
  GlobeIcon,
  PinIcon,
} from "@/components/icons";

const FENETRE_STYLE: Record<string, { badge: string; accent: string }> = {
  "EN COURS": {
    badge: "bg-emerald-100 text-emerald-800 ring-emerald-600/20",
    accent: "bg-emerald-500",
  },
  IMMINENT: {
    badge: "bg-amber-100 text-amber-800 ring-amber-600/20",
    accent: "bg-amber-500",
  },
  "BIENTÔT": {
    badge: "bg-sky-100 text-sky-800 ring-sky-600/20",
    accent: "bg-sky-500",
  },
  "ANNONCÉ": {
    badge: "bg-indigo-50 text-indigo-700 ring-indigo-600/20",
    accent: "bg-indigo-400",
  },
  INCONNUE: {
    badge: "bg-gray-100 text-gray-600 ring-gray-500/20",
    accent: "bg-gray-300",
  },
};

function Badge({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${className}`}
    >
      {children}
    </span>
  );
}

function formatDate(iso: string | null): string {
  if (!iso) return "date non précisée";
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d}/${m}/${y}`;
}

function formatRange(debut: string | null, fin: string | null) {
  if (!debut && !fin) return "Date à confirmer";
  if (debut && fin && debut !== fin)
    return `${formatDate(debut)} → ${formatDate(fin)}`;
  return formatDate(debut || fin);
}

export function HackathonCard({ h }: { h: Hackathon }) {
  const style = FENETRE_STYLE[h.fenetre] ?? FENETRE_STYLE.INCONNUE;
  const estEnCours = h.fenetre === "EN COURS";

  return (
    <Link
      href={`/hackathon/${h.slug}`}
      className="group relative flex flex-col gap-3 overflow-hidden rounded-xl border border-gray-200 bg-white p-4 pl-5 shadow-sm transition duration-150 hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
    >
      <span
        className={`absolute inset-y-0 left-0 w-1.5 ${style.accent}`}
        aria-hidden
      />

      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-gray-900 group-hover:text-indigo-700 line-clamp-2">
          {h.titre}
        </h3>
        {estEnCours ? null : (
          <Badge className={`shrink-0 ${style.badge}`}>{h.fenetre}</Badge>
        )}
      </div>

      <div className="text-sm text-gray-600">
        <span className="font-medium text-gray-800">
          {h.organisateur || "Organisateur non précisé"}
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          {h.en_ligne ? (
            <>
              <GlobeIcon className="h-3.5 w-3.5" />
              En ligne
            </>
          ) : (
            <>
              <PinIcon className="h-3.5 w-3.5" />
              {h.ville || "Maroc"}
            </>
          )}
        </span>
        <span className="inline-flex items-center gap-1">
          <CalendarIcon className="h-3.5 w-3.5" />
          {formatRange(h.date_debut, h.date_fin)}
        </span>
      </div>

      {h.description ? (
        <p className="line-clamp-2 text-sm text-gray-500">{h.description}</p>
      ) : null}

      <div className="mt-auto flex flex-wrap items-center gap-1.5 pt-1">
        <Badge className="bg-indigo-50 text-indigo-700 ring-indigo-600/20">
          {h.domaine || "Généraliste"}
        </Badge>
        {h.en_ligne ? (
          <Badge className="bg-fuchsia-50 text-fuchsia-700 ring-fuchsia-600/20">
            En ligne
          </Badge>
        ) : null}
      </div>

      <div className="flex items-center justify-between border-t border-gray-100 pt-2 text-xs text-gray-400">
        <span>{h.source}</span>
        <ArrowRightIcon className="h-3 w-3 text-gray-300 transition group-hover:text-indigo-400" />
      </div>

      {estEnCours ? (
        <span className="absolute -right-8 top-3 rotate-45 bg-emerald-500 px-8 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white shadow-sm">
          En cours
        </span>
      ) : null}
    </Link>
  );
}

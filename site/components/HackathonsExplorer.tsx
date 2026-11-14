"use client";

import { useMemo, useState } from "react";
import type { Hackathon } from "@/lib/db";
import { HackathonCard } from "./HackathonCard";

const PAGE_SIZE = 24;
const FENETRES = ["EN COURS", "IMMINENT", "BIENTÔT", "ANNONCÉ", "INCONNUE"];
const FORMATS = ["Tous", "En ligne", "Présentiel"];

export default function HackathonsExplorer({ items }: { items: Hackathon[] }) {
  const [q, setQ] = useState("");
  const [fenetre, setFenetre] = useState<string>("");
  const [domaine, setDomaine] = useState<string>("");
  const [ville, setVille] = useState<string>("");
  const [format, setFormat] = useState<string>("Tous");
  const [page, setPage] = useState(1);

  const domaines = useMemo(
    () =>
      Array.from(new Set(items.map((h) => h.domaine).filter(Boolean))).sort() as string[],
    [items]
  );
  const villes = useMemo(
    () =>
      Array.from(new Set(items.map((h) => h.ville).filter(Boolean))).sort() as string[],
    [items]
  );

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return items.filter((h) => {
      if (fenetre && h.fenetre !== fenetre) return false;
      if (domaine && h.domaine !== domaine) return false;
      if (ville && h.ville !== ville) return false;
      if (format === "En ligne" && !h.en_ligne) return false;
      if (format === "Présentiel" && h.en_ligne) return false;
      if (ql) {
        const hay = `${h.titre} ${h.organisateur ?? ""} ${h.description ?? ""}`.toLowerCase();
        if (!hay.includes(ql)) return false;
      }
      return true;
    });
  }, [items, q, fenetre, domaine, ville, format]);

  const visible = filtered.slice(0, page * PAGE_SIZE);

  const resetFilters = () => {
    setQ("");
    setFenetre("");
    setDomaine("");
    setVille("");
    setFormat("Tous");
    setPage(1);
  };

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-6 gap-3 mb-6">
        <input
          type="search"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPage(1);
          }}
          placeholder="Rechercher…"
          className="md:col-span-2 border border-[color:var(--border)] rounded px-3 py-2 bg-transparent"
        />
        <select
          value={fenetre}
          onChange={(e) => {
            setFenetre(e.target.value);
            setPage(1);
          }}
          className="border border-[color:var(--border)] rounded px-3 py-2 bg-transparent"
        >
          <option value="">Toutes fenêtres</option>
          {FENETRES.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
        <select
          value={domaine}
          onChange={(e) => {
            setDomaine(e.target.value);
            setPage(1);
          }}
          className="border border-[color:var(--border)] rounded px-3 py-2 bg-transparent"
        >
          <option value="">Tous domaines</option>
          {domaines.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <select
          value={ville}
          onChange={(e) => {
            setVille(e.target.value);
            setPage(1);
          }}
          className="border border-[color:var(--border)] rounded px-3 py-2 bg-transparent"
        >
          <option value="">Toutes villes</option>
          {villes.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
        <select
          value={format}
          onChange={(e) => {
            setFormat(e.target.value);
            setPage(1);
          }}
          className="border border-[color:var(--border)] rounded px-3 py-2 bg-transparent"
        >
          {FORMATS.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center justify-between mb-4 text-sm text-[color:var(--muted)]">
        <span>
          {filtered.length} résultat{filtered.length > 1 ? "s" : ""}
        </span>
        {(q || fenetre || domaine || ville || format !== "Tous") && (
          <button
            onClick={resetFilters}
            className="underline hover:text-[color:var(--foreground)]"
          >
            Réinitialiser
          </button>
        )}
      </div>

      {filtered.length === 0 ? (
        <p className="text-center text-[color:var(--muted)] py-16">
          Aucun hackathon ne correspond à ces filtres.
        </p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visible.map((h) => (
              <HackathonCard key={h.slug} h={h} />
            ))}
          </div>
          {visible.length < filtered.length && (
            <div className="text-center mt-8">
              <button
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 border border-[color:var(--border)] rounded hover:border-[color:var(--accent)]"
              >
                Voir plus ({filtered.length - visible.length} restants)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

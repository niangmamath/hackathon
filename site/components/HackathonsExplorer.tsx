"use client";

import { useEffect, useMemo, useState } from "react";
import type { Hackathon } from "@/lib/db";
import { HackathonCard } from "./HackathonCard";
import { FlashIcon, SearchIcon } from "./icons";

const TOUS = "Tous";
const PAR_PAGE = 24;
const FENETRES = [TOUS, "EN COURS", "IMMINENT", "BIENTÔT", "ANNONCÉ"];
const FORMATS = [TOUS, "En ligne", "Présentiel"];

function uniqueSorted(values: (string | null)[]): string[] {
  return Array.from(new Set(values.filter((v): v is string => !!v))).sort(
    (a, b) => a.localeCompare(b, "fr")
  );
}

function formatMaj(iso: string | null): string {
  if (!iso) return "jamais";
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "Africa/Casablanca",
  });
}

export default function HackathonsExplorer({
  items,
  derniereMaj,
}: {
  items: Hackathon[];
  derniereMaj: string | null;
}) {
  const [recherche, setRecherche] = useState("");
  const [fenetre, setFenetre] = useState(TOUS);
  const [domaine, setDomaine] = useState(TOUS);
  const [ville, setVille] = useState(TOUS);
  const [format, setFormat] = useState(TOUS);
  const [visibles, setVisibles] = useState(PAR_PAGE);

  const domaines = useMemo(
    () => [TOUS, ...uniqueSorted(items.map((h) => h.domaine))],
    [items]
  );
  const villes = useMemo(
    () => [TOUS, ...uniqueSorted(items.map((h) => h.ville))],
    [items]
  );

  const enCours = useMemo(
    () => items.filter((h) => h.fenetre === "EN COURS").length,
    [items]
  );
  const enLigne = useMemo(() => items.filter((h) => h.en_ligne).length, [items]);

  const filtrees = useMemo(() => {
    const q = recherche.trim().toLowerCase();
    return items.filter((h) => {
      if (fenetre !== TOUS && h.fenetre !== fenetre) return false;
      if (domaine !== TOUS && h.domaine !== domaine) return false;
      if (ville !== TOUS && h.ville !== ville) return false;
      if (format === "En ligne" && !h.en_ligne) return false;
      if (format === "Présentiel" && h.en_ligne) return false;
      if (q) {
        const blob =
          `${h.titre} ${h.organisateur ?? ""} ${h.description ?? ""}`.toLowerCase();
        if (!blob.includes(q)) return false;
      }
      return true;
    });
  }, [items, recherche, fenetre, domaine, ville, format]);

  useEffect(() => {
    setVisibles(PAR_PAGE);
  }, [recherche, fenetre, domaine, ville, format]);

  const affichees = filtrees.slice(0, visibles);

  return (
    <>
      {/* Hero */}
      <header className="relative overflow-hidden bg-gradient-to-br from-indigo-700 via-violet-700 to-fuchsia-700">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-20 [background-image:radial-gradient(circle_at_15%_10%,white,transparent_30%),radial-gradient(circle_at_85%_0%,white,transparent_25%)]"
        />
        <div className="relative mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              <FlashIcon className="h-6 w-6 shrink-0 sm:h-7 sm:w-7" />
              Hackathons au Maroc
            </h1>
            <p className="text-xs text-indigo-200">
              Mis à jour : {formatMaj(derniereMaj)}
            </p>
          </div>
          <p className="mt-1 max-w-xl text-sm text-indigo-100">
            Hackathons, datathons, ideathons et CTF — au Maroc et en ligne.
            Veille automatique, tous domaines.
          </p>

          <div className="relative mt-4 max-w-2xl">
            <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="search"
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              placeholder="Rechercher un hackathon, un organisateur…"
              className="w-full rounded-full border-0 bg-white py-3 pl-12 pr-4 text-sm text-gray-900 shadow-lg outline-none ring-1 ring-black/5 placeholder:text-gray-400 focus:ring-2 focus:ring-white sm:text-base"
            />
          </div>

          {items.length > 0 ? (
            <p className="mt-3 text-xs text-indigo-100 sm:text-sm">
              <span className="font-semibold text-white">{items.length}</span>{" "}
              hackathon{items.length !== 1 ? "s" : ""} suivi
              {items.length !== 1 ? "s" : ""}
              {" · "}
              <span className="font-semibold text-white">{enCours}</span> en
              cours
              {" · "}
              <span className="font-semibold text-white">{enLigne}</span> en
              ligne
            </p>
          ) : null}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
        <div className="flex flex-col gap-6">
          {/* Filtres sticky */}
          <div className="sticky top-3 z-10 flex flex-col gap-3 rounded-xl border border-gray-200 bg-white/95 p-3 shadow-sm backdrop-blur sm:flex-row sm:flex-wrap sm:items-center">
            <Select
              label="Fenêtre"
              value={fenetre}
              onChange={setFenetre}
              options={FENETRES}
            />
            <Select
              label="Domaine"
              value={domaine}
              onChange={setDomaine}
              options={domaines}
            />
            <Select
              label="Ville"
              value={ville}
              onChange={setVille}
              options={villes}
            />
            <Select
              label="Format"
              value={format}
              onChange={setFormat}
              options={FORMATS}
            />
          </div>

          <p className="text-sm text-gray-500">
            <span className="font-semibold text-gray-700">
              {filtrees.length}
            </span>{" "}
            hackathon{filtrees.length !== 1 ? "s" : ""} affiché
            {filtrees.length !== 1 ? "s" : ""} sur {items.length}
          </p>

          {filtrees.length === 0 ? (
            <div className="rounded-xl border border-dashed border-gray-300 p-10 text-center text-sm text-gray-500">
              Aucun hackathon ne correspond à ces critères.
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {affichees.map((h) => (
                  <HackathonCard key={h.slug} h={h} />
                ))}
              </div>
              {visibles < filtrees.length ? (
                <button
                  type="button"
                  onClick={() => setVisibles((v) => v + PAR_PAGE)}
                  className="mx-auto rounded-full border border-gray-300 bg-white px-6 py-2.5 text-sm font-semibold text-gray-700 shadow-sm transition hover:bg-gray-50"
                >
                  Voir plus ({filtrees.length - visibles} restants)
                </button>
              ) : null}
            </>
          )}
        </div>
      </main>
    </>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <label className="flex items-center gap-2 text-sm text-gray-600">
      <span className="hidden sm:inline">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-gray-300 px-2.5 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

import { getHackathons, getDerniereMaj } from "@/lib/db";
import HackathonsExplorer from "@/components/HackathonsExplorer";

export const revalidate = 3600;

export default async function HomePage() {
  const [items, maj] = await Promise.all([getHackathons(), getDerniereMaj()]);

  if (items === null) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-20 text-center">
        <h1 className="text-2xl font-semibold mb-3">
          Site en cours de configuration
        </h1>
        <p className="text-[color:var(--muted)]">
          La variable <code>DATABASE_URL</code> n&apos;est pas encore définie.
          Renseignez-la dans les variables d&apos;environnement Vercel puis
          redéployez.
        </p>
      </div>
    );
  }

  const nbOnline = items.filter((h) => h.en_ligne).length;
  const nbPhysique = items.length - nbOnline;
  const nbEnCours = items.filter((h) => h.fenetre === "EN COURS").length;

  return (
    <>
      {/* Hero */}
      <section className="bg-[color:var(--surface)] border-b border-[color:var(--border)]">
        <div className="max-w-6xl mx-auto px-5 py-12 sm:py-16">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-3">
            Hackathons au Maroc & en ligne
          </h1>
          <p className="text-[color:var(--muted)] text-base sm:text-lg max-w-2xl">
            Toute la veille tech marocaine — hackathons, datathons, ideathons
            et CTF — en un seul endroit. Mise à jour automatique tous les 2
            jours.
          </p>

          <div className="mt-8 grid grid-cols-3 gap-3 sm:gap-6 max-w-2xl">
            <Stat value={items.length} label="suivis" />
            <Stat value={nbEnCours} label="en cours" accent />
            <Stat value={nbOnline} label="en ligne" />
          </div>

          {maj && (
            <p className="mt-6 text-xs text-[color:var(--muted)]">
              Dernière mise à jour :{" "}
              {new Date(maj).toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
          )}
        </div>
      </section>

      {/* Liste */}
      <section className="max-w-6xl mx-auto px-5 py-10">
        <HackathonsExplorer items={items} />
      </section>
    </>
  );
}

function Stat({
  value,
  label,
  accent = false,
}: {
  value: number;
  label: string;
  accent?: boolean;
}) {
  return (
    <div className="card p-4">
      <div
        className={`text-2xl sm:text-3xl font-bold tabular-nums ${accent ? "text-[color:var(--accent)]" : ""}`}
      >
        {value}
      </div>
      <div className="text-xs sm:text-sm text-[color:var(--muted)] mt-0.5">
        {label}
      </div>
    </div>
  );
}

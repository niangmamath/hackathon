import { getHackathons, getDerniereMaj } from "@/lib/db";
import HackathonsExplorer from "@/components/HackathonsExplorer";

// La veille tourne toutes les ~48h ; 1h de revalidation est largement
// suffisant pour refléter les nouvelles insertions côté site.
export const revalidate = 3600;

export default async function HomePage() {
  const [items, maj] = await Promise.all([getHackathons(), getDerniereMaj()]);

  if (items === null) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-semibold mb-3">
          Site en cours de configuration
        </h1>
        <p className="text-[color:var(--muted)]">
          La variable <code>DATABASE_URL</code> n&apos;est pas encore
          définie. Renseignez-la dans les variables d&apos;environnement
          Vercel (Neon, chaîne pooled, port 6543) puis redéployez.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Hackathons au Maroc & en ligne
        </h1>
        <p className="text-[color:var(--muted)]">
          Veille automatique — {items.length} hackathon
          {items.length > 1 ? "s" : ""} suivi
          {items.length > 1 ? "s" : ""} (
          {items.filter((h) => h.en_ligne).length} en ligne,{" "}
          {items.filter((h) => !h.en_ligne).length} au Maroc).
          {maj && (
            <>
              {" "}Dernière mise à jour :{" "}
              {new Date(maj).toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
              .
            </>
          )}
        </p>
      </div>
      <HackathonsExplorer items={items} />
    </div>
  );
}

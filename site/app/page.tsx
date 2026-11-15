import { getHackathons, getDerniereMaj, type Hackathon } from "@/lib/db";
import HackathonsExplorer from "@/components/HackathonsExplorer";
import { FlashIcon } from "@/components/icons";
import { siteUrl } from "@/lib/site-url";

export const revalidate = 3600;

// ItemList JSON-LD — liste des hackathons avec leur URL interne, pour
// aider Google à comprendre la structure de la page. Google n'affiche
// pas forcément de rich result pour une page de LISTING (il préfère les
// Event isolés sur la page détail), mais le signal structuré ne coûte
// rien et aide l'indexation.
function ItemListJsonLd({ items }: { items: Hackathon[] }) {
  const json = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: items.slice(0, 50).map((h, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${siteUrl}/hackathon/${h.slug}`,
      name: h.titre,
    })),
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}

export default async function HomePage() {
  const [items, maj] = await Promise.all([getHackathons(), getDerniereMaj()]);

  if (items === null) {
    return (
      <div className="flex min-h-full flex-col">
        <header className="bg-gradient-to-br from-indigo-700 via-violet-700 to-fuchsia-700 px-4 py-8 sm:px-6">
          <h1 className="flex items-center gap-2 text-2xl font-extrabold text-white sm:text-3xl">
            <FlashIcon className="h-6 w-6 shrink-0" />
            Hackathons au Maroc
          </h1>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
            Base de données non configurée (variable{" "}
            <code>DATABASE_URL</code> absente). Renseignez-la dans les
            variables d&apos;environnement Vercel puis redéployez.
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-col">
      {items.length > 0 ? <ItemListJsonLd items={items} /> : null}
      <HackathonsExplorer items={items} derniereMaj={maj} />
      <footer className="mt-auto border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-6 text-center text-xs text-gray-400 sm:px-6">
          Événements collectés automatiquement (Devpost, MLH) — vérifiez
          toujours les conditions d&apos;inscription auprès de
          l&apos;organisateur avant de participer.
        </div>
      </footer>
    </div>
  );
}

# Site Hackathons Maroc

Next.js 16 (App Router) + Tailwind v4 + `pg` pour lire la base Neon
peuplée par le pipeline Python du dépôt parent.

## Dev local

```bash
npm install
cp .env.local.example .env.local   # renseigner DATABASE_URL (chaîne pooled Neon)
npm run dev                         # http://localhost:3000
```

## Déploiement Vercel

1. Importer le dépôt `niangmamath/hackathon` sur Vercel.
2. **Root Directory → `site`** (sinon Vercel essaie de déployer le script
   Python de la racine et échoue avec `PYTHON_ENTRYPOINT_NOT_FOUND`).
3. Variables d'environnement :
   - `DATABASE_URL` — **chaîne pooled Neon** (celle qui contient
     `-pooler.`, port 6543) — Vercel est serverless, on utilise le
     pooler pour éviter de saturer Postgres.
4. Deploy. Vercel détecte Next.js, exécute `npm run build` puis sert.

## Architecture

- `lib/pg.ts` — pool pg partagé (globalThis-cached pour survivre aux
  hot-reloads).
- `lib/db.ts` — requêtes SELECT (`getHackathons`, `getHackathonBySlug`,
  `getDerniereMaj`). Retourne `null` si `DATABASE_URL` absente — la
  page home affiche alors un message explicite plutôt que de planter.
- `app/page.tsx` — liste serveur (revalidate 1h, la veille tourne toutes
  les 48h de toute façon).
- `app/hackathon/[slug]/page.tsx` — détail avec JSON-LD
  `schema.org/Event` pour les rich results Google.
- `components/HackathonsExplorer.tsx` — filtres (fenêtre, domaine, ville,
  format) + recherche + pagination "Voir plus" côté client.
- `app/sitemap.ts` + `app/robots.ts` — SEO prêt.

Ni admin ni newsletter en v1 (contrairement au site stages-maroc) — à
ajouter plus tard si besoin.

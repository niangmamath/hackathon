// Adresse publique du site (liens du sitemap, canonical, OpenGraph).
//
// Ordre :
//   1. NEXT_PUBLIC_SITE_URL      — nom de domaine final, à poser quand on
//      en aura un (surpasse tout le reste).
//   2. VERCEL_PROJECT_PRODUCTION_URL — domaine de PRODUCTION stable fourni
//      par Vercel (ex. hackathon-mamath-yacines-projects.vercel.app), ne
//      change pas entre deux déploiements.
//   3. VERCEL_URL                 — l'URL temporaire du déploiement courant
//      (hash-xxxxx.vercel.app). À n'utiliser qu'en dernier recours : elle
//      change à chaque push et pollue sitemap/canonical si elle y arrive.
//   4. localhost (dev local).
export const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : process.env.VERCEL_URL
      ? `https://${process.env.VERCEL_URL}`
      : "http://localhost:3000");

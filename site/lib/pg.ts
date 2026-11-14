import { Pool } from "pg";

// Pool unique partagé par toutes les routes (globalThis survit aux
// Hot Reloads en dev et aux ré-exécutions de modules côté serverless).
// `max` volontairement bas : Neon pooler accepte beaucoup de connexions
// simultanées, mais chaque instance Vercel serverless multiplie le nombre
// de pools ouverts — mieux vaut rester prudent pour éviter le plafond
// du plan gratuit Neon.
const globalForPg = globalThis as unknown as { _pgPoolPartage?: Pool };

export function getPool(): Pool | null {
  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) return null;
  if (!globalForPg._pgPoolPartage) {
    const local =
      connectionString.includes("localhost") ||
      connectionString.includes("127.0.0.1");
    globalForPg._pgPoolPartage = new Pool({
      connectionString,
      ssl: local ? false : { rejectUnauthorized: false },
      max: 5,
    });
  }
  return globalForPg._pgPoolPartage;
}

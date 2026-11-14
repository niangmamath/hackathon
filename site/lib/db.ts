import { getPool } from "./pg";

export type Hackathon = {
  url: string;
  slug: string;
  titre: string;
  organisateur: string | null;
  ville: string | null;
  description: string | null;
  domaine: string | null;
  source: string | null;
  date_debut: string | null;
  date_fin: string | null;
  en_ligne: boolean;
  fenetre: string;
  premiere_detection: string;
  derniere_verification: string;
};

const SELECT = `
  SELECT url, slug, titre, organisateur, ville, description, domaine,
         source, to_char(date_debut, 'YYYY-MM-DD') AS date_debut,
         to_char(date_fin, 'YYYY-MM-DD') AS date_fin,
         en_ligne, fenetre, premiere_detection, derniere_verification
  FROM hackathons
  WHERE masque = FALSE
`;

/** null = DATABASE_URL absente — distinct d'une liste vide (base
 * connectée mais aucun hackathon pour l'instant). */
export async function getHackathons(): Promise<Hackathon[] | null> {
  const pool = getPool();
  if (!pool) return null;
  // Tri par imminence : EN COURS -> IMMINENT -> BIENTÔT -> ANNONCÉ ->
  // INCONNUE, puis par date de début croissante (le plus proche d'abord).
  const { rows } = await pool.query<Hackathon>(
    `${SELECT}
     ORDER BY
       CASE fenetre
         WHEN 'EN COURS' THEN 0
         WHEN 'IMMINENT' THEN 1
         WHEN 'BIENTÔT' THEN 2
         WHEN 'ANNONCÉ' THEN 3
         WHEN 'INCONNUE' THEN 4
         ELSE 9
       END,
       date_debut ASC NULLS LAST,
       premiere_detection DESC`
  );
  return rows;
}

export async function getHackathonBySlug(slug: string): Promise<Hackathon | null> {
  const pool = getPool();
  if (!pool) return null;
  const { rows } = await pool.query<Hackathon>(
    `${SELECT} AND slug = $1 LIMIT 1`,
    [slug]
  );
  return rows[0] ?? null;
}

export async function getDerniereMaj(): Promise<string | null> {
  const pool = getPool();
  if (!pool) return null;
  const { rows } = await pool.query<{ max: string | null }>(
    "SELECT MAX(derniere_verification) AS max FROM hackathons"
  );
  return rows[0]?.max ?? null;
}

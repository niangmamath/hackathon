# -*- coding: utf-8 -*-
"""Synchronisation des hackathons CONVENABLES vers une base Postgres
(Supabase) — même pattern que sourcing-stages-maroc/db_sync.py.

Dégrade proprement : si `psycopg2` n'est pas installé ou si `DATABASE_URL`
n'est pas définie, `sync()` affiche un message et ne fait rien (un run
local sans base configurée reste utile pour tester le classifieur).

Contrat : la table est traitée comme le reflet de "ce qui est actuellement
convenable" — upsert des convenables, suppression des hackathons qui ne
le sont plus (passés, retirés par l'organisateur). `manuel = TRUE` protège
une ligne ajoutée à la main depuis l'admin du site (même convention que
pour les stages).
"""
import datetime as dt
import hashlib
import os
import re
import unicodedata


TABLE_SQL = """
CREATE TABLE IF NOT EXISTS hackathons (
    url TEXT PRIMARY KEY,
    titre TEXT NOT NULL,
    organisateur TEXT,
    ville TEXT,
    description TEXT,
    domaine TEXT,
    source TEXT,
    date_debut DATE,
    date_fin DATE,
    en_ligne BOOLEAN NOT NULL DEFAULT FALSE,
    fenetre TEXT,
    slug TEXT,
    premiere_detection TIMESTAMPTZ NOT NULL DEFAULT now(),
    derniere_verification TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

MIGRATIONS_SQL = [
    "CREATE UNIQUE INDEX IF NOT EXISTS hackathons_slug_idx ON hackathons (slug)",
    # masque / manuel : réservés à l'admin du site, volontairement absents
    # du UPSERT pour ne JAMAIS être écrasés par un run de scraping.
    "ALTER TABLE hackathons ADD COLUMN IF NOT EXISTS masque BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE hackathons ADD COLUMN IF NOT EXISTS manuel BOOLEAN NOT NULL DEFAULT FALSE",
]

UPSERT_SQL = """
INSERT INTO hackathons (
    url, titre, organisateur, ville, description, domaine, source,
    date_debut, date_fin, en_ligne, fenetre, slug,
    premiere_detection, derniere_verification
) VALUES (
    %(url)s, %(titre)s, %(organisateur)s, %(ville)s, %(description)s,
    %(domaine)s, %(source)s, %(date_debut)s, %(date_fin)s, %(en_ligne)s,
    %(fenetre)s, %(slug)s,
    %(premiere_detection)s, %(derniere_verification)s
)
ON CONFLICT (url) DO UPDATE SET
    titre = EXCLUDED.titre, organisateur = EXCLUDED.organisateur,
    ville = EXCLUDED.ville, description = EXCLUDED.description,
    domaine = EXCLUDED.domaine, source = EXCLUDED.source,
    date_debut = EXCLUDED.date_debut, date_fin = EXCLUDED.date_fin,
    en_ligne = EXCLUDED.en_ligne, fenetre = EXCLUDED.fenetre,
    derniere_verification = EXCLUDED.derniere_verification
    -- premiere_detection et slug volontairement absents du UPDATE :
    -- stables une fois posés (même raisonnement que sourcing-stages-maroc).
"""


def _slug(url, titre):
    base = unicodedata.normalize("NFKD", titre or "")
    base = "".join(c for c in base if not unicodedata.combining(c))
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()[:60]
    suffixe = hashlib.sha1((url or "").encode("utf-8")).hexdigest()[:8]
    return f"{base}-{suffixe}" if base else suffixe


def _iso_or_none(s):
    if not s:
        return None
    s = str(s).strip()[:10]
    try:
        dt.date.fromisoformat(s)
        return s
    except ValueError:
        return None


def _ts_or_now(s):
    """Parse une 'première détection' au format ISO (YYYY-MM-DD) posée par
    hackathons_maroc._update_vues ; retombe sur maintenant si le format
    est inattendu, plutôt que de planter le run."""
    if not s:
        return dt.datetime.now()
    try:
        return dt.datetime.fromisoformat(str(s))
    except ValueError:
        # Format court YYYY-MM-DD -> ok sous ISO 8601 par fromisoformat depuis Py 3.11
        try:
            return dt.datetime.strptime(str(s)[:10], "%Y-%m-%d")
        except ValueError:
            return dt.datetime.now()


def _row(a):
    url = a.get("url") or ""
    titre = a.get("poste", "")
    return {
        "url": url,
        "titre": titre,
        "organisateur": a.get("entite", ""),
        "ville": a.get("ville", ""),
        "description": (a.get("texte") or "")[:2000],
        "domaine": a.get("domaine", "Généraliste"),
        "source": a.get("source", ""),
        "date_debut": _iso_or_none(a.get("date_debut")),
        "date_fin": _iso_or_none(a.get("date_fin")),
        "en_ligne": bool(a.get("en_ligne")),
        "fenetre": a.get("fenetre", "INCONNUE"),
        "slug": _slug(url, titre),
        "premiere_detection": _ts_or_now(a.get("premiere_detection")),
        "derniere_verification": _ts_or_now(a.get("derniere_verif")),
    }


def sync(items, database_url=None):
    """Upsert des hackathons convenables, purge de ceux qui ne le sont plus.
    items : liste classée (sortie de `classify_all`) ; seuls ceux avec un
    `url` non vide ET `verdict == CONVENABLE` sont envoyés."""
    database_url = database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        print("  [db] DATABASE_URL non définie — synchro ignorée.")
        return

    try:
        import psycopg2
    except ImportError:
        print("  [db] psycopg2 non installé (pip install psycopg2-binary) "
              "— synchro ignorée.")
        return

    convenables = [a for a in items
                   if a.get("verdict") == "CONVENABLE" and a.get("url")]
    urls_gardees = {a["url"] for a in convenables}

    try:
        conn = psycopg2.connect(database_url)
        try:
            with conn.cursor() as cur:
                cur.execute(TABLE_SQL)
                for migration in MIGRATIONS_SQL:
                    cur.execute(migration)
                for a in convenables:
                    cur.execute(UPSERT_SQL, _row(a))
                if urls_gardees:
                    cur.execute(
                        "DELETE FROM hackathons "
                        "WHERE url != ALL(%s) AND manuel = FALSE",
                        (list(urls_gardees),))
                else:
                    cur.execute(
                        "DELETE FROM hackathons WHERE manuel = FALSE")
                supprimes = cur.rowcount
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"  [db] ERREUR synchro base : {e}")
        # Code de sortie non nul : le workflow passe en échec (et GitHub
        # envoie une alerte) au lieu d'afficher un succès trompeur.
        # Constaté du 21/11 au 25/11/2026 : mot de passe Neon invalide,
        # site figé, runs pourtant verts.
        raise SystemExit(1) from e

    print(f"  [db] {len(convenables)} hackathon(s) synchronisé(s) "
          f"({supprimes} retiré(s) car plus convenable(s)).")

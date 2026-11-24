# Veille des hackathons — Maroc (+ en ligne)

Pipeline Python de détection des **hackathons, datathons, ideathons, CTF et
game jams** se tenant au Maroc, OU en ligne et accessibles depuis le Maroc.
Projet frère de `sourcing-stages-maroc` : même architecture (collecteurs
best-effort + classifieur pur + synchro Postgres/Neon + cache JSON),
adaptée au cycle de vie d'un **événement ponctuel** (date de début/fin)
plutôt que d'une offre d'emploi (fenêtre de publication).

La sortie est une **table Postgres** (pas un Excel) : contrairement à
`sourcing-regie-banque`, il n'y a pas d'annotations manuelles à préserver
ici — le reflet "ce qui est convenable aujourd'hui" est entièrement
produit par le pipeline, donc une base lue en direct par un site web est
le bon support (même choix que `sourcing-stages-maroc`).

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Aucune clé API requise pour la collecte (toutes les sources sont des
pages publiques). Pour la synchro base de données, renseigner
`DATABASE_URL` (connection string Postgres / Supabase) en variable
d'environnement ou dans un `.env` à la racine.

## Usage

```bash
python hackathons_maroc.py            # collecte réseau + upsert Postgres
python hackathons_maroc.py reclass    # re-classe depuis le cache, hors ligne
```

Sans `DATABASE_URL` ou sans `psycopg2`, le pipeline dégrade proprement :
il tourne, classe, met à jour `cache_hackathons.json` + `annonces_vues.json`,
mais la synchro base est sautée (message explicite).

## Sources (v1)

| Source | Accès | Portée |
|---|---|---|
| **Devpost** | scraping de `/hackathons` (tuiles React → JSON embarqué) | gros catalogue mondial, dont beaucoup d'événements **en ligne** ouverts worldwide |
| **MLH** | HTML statique `mlh.io/seasons/.../events` | hackathons étudiants, mondial, dates fermes |
| **Eventbrite** | HTML `/d/morocco/hackathon/` (`JSON-LD` Event embarqué) | événements **présentiels au Maroc** publiés sur Eventbrite |

Pour ajouter une source (ex. Technopark, UM6P, universités marocaines) :
écrire une fonction `collect_xxx()` dans `sources.py` qui renvoie une liste
de dicts aux mêmes clés, puis l'ajouter au registre `COLLECTORS`.

Sources évaluées et écartées en v1 :
- **LinkedIn Events** : non exposé par `jobs-guest`, exigerait une session
  connectée (comme pour les stages, l'endpoint `jobs-guest` ne couvre que
  les emplois).
- **Instagram / X** : canal réel mais pas scrapable proprement sans API
  payante / compte.
- **Meetup** : son API a été fermée au public gratuit en 2019.

## Comment un événement devient « convenable »

Logique dans `classifier.py` (pur, testé). Un événement est **CONVENABLE**
si les trois conditions sont vraies, sinon **ÉCARTÉE** (avec motif) :

1. **C'est un hackathon** — mot-clé fort dans le titre (`hackathon`,
   `datathon`, `ideathon`, `ctf`, `coding challenge`...) suffit ; sinon
   un mot-clé faible (`innovation challenge`, `startup weekend`...) doit
   être accompagné d'un signal de compétition organisée (`48h`, `jury`,
   `pitch`, `prize`...). Garde-fou : bootcamps, meetups, conférences,
   forums de recrutement ne sont PAS requalifiés en hackathons même si
   le mot "hack" apparaît dans le texte.
2. **C'est accessible depuis le Maroc** — événement présentiel au Maroc
   OU événement en ligne (`online`, `virtual`, `worldwide`...). Un
   hackathon présentiel à Paris/Dubaï/Abidjan sans mention "online" est
   écarté.
3. **L'événement n'est pas passé** — si la date de fin est révolue, il
   est écarté (différence importante avec `sourcing-stages-maroc` : ici
   la fraîcheur se calcule sur la date d'**événement**, pas la date de
   **publication** de l'annonce).

Le **domaine** (IA/Data, Fintech, Cybersécurité, HealthTech, GreenTech,
EdTech, Mobilité, GovTech, Généraliste) est un **tag informatif** —
jamais un critère d'exclusion.

### Fenêtre de fraîcheur (colonne `Fenêtre` de l'Excel)

Calculée à partir de la date de début (fin à défaut), relative à
aujourd'hui :

| Fenêtre | Règle |
|---|---|
| EN COURS | `début ≤ aujourd'hui ≤ fin` |
| IMMINENT | `début ≤ aujourd'hui + 7 j` |
| BIENTÔT | `début ≤ aujourd'hui + 30 j` |
| ANNONCÉ | `début > aujourd'hui + 30 j` |
| INCONNUE | pas de date utilisable (n'écarte rien, remonte juste le doute) |
| PASSÉ | `fin < aujourd'hui` → écarté |

## Sortie — table Postgres `hackathons`

Schéma créé automatiquement au premier run (voir `db_sync.TABLE_SQL`) :

| Colonne | Type | Rôle |
|---|---|---|
| `url` | TEXT **PK** | identifiant stable (déduplique inter-runs) |
| `titre` | TEXT | nom de l'événement |
| `organisateur` | TEXT | société/école/collectif qui organise |
| `ville` | TEXT | ville canonique, `En ligne` ou `Maroc (non précisé)` |
| `description` | TEXT | résumé (tronqué à 2000 caractères) |
| `domaine` | TEXT | IA/Data, Fintech, Cybersécurité, HealthTech, GreenTech, EdTech, Mobilité, GovTech, Généraliste |
| `source` | TEXT | Devpost / MLH / Eventbrite |
| `date_debut`, `date_fin` | DATE | dates de l'événement (NULL si inconnues) |
| `en_ligne` | BOOLEAN | événement accessible à distance |
| `fenetre` | TEXT | EN COURS / IMMINENT / BIENTÔT / ANNONCÉ / INCONNUE |
| `slug` | TEXT **UNIQUE** | identifiant d'URL stable pour la page de détail |
| `premiere_detection`, `derniere_verification` | TIMESTAMPTZ | historique |
| `masque`, `manuel` | BOOLEAN | **réservés à l'admin du site**, jamais écrasés par le scraping |

À chaque run, les hackathons convenables sont upsertés ; ceux qui ne
sont plus convenables (passés, retirés par l'organisateur) sont supprimés,
sauf si `manuel = TRUE`.

**Déduplication inter-sources** : `classifier.dedup_annonces()` fusionne
les événements apparus simultanément sur plusieurs sources (clé :
organisateur + titre normalisé, insensible à la casse/aux accents).

## Mise en route Neon

1. Créer un projet sur [neon.tech](https://neon.tech) (gratuit).
2. Dashboard Neon → **Connection Details** → copier la *Connection
   string* (déjà au format `postgresql://.../neondb?sslmode=require`).
   Garder le `?sslmode=require` tel quel : Neon refuse les connexions non
   chiffrées, et psycopg2 ne force pas le TLS tout seul.
3. La poser dans `DATABASE_URL` :
   - **Local** : `cp .env.example .env`, puis coller la vraie valeur dans
     `.env` (jamais commité).
   - **CI (GitHub Actions)** : Settings → Secrets and variables →
     Actions → `DATABASE_URL`.
4. Pas besoin d'exécuter manuellement le `CREATE TABLE` : le pipeline
   crée la table `hackathons` au premier run (`db_sync.TABLE_SQL`), avec
   migrations additives idempotentes.

> Pour un futur site Next.js lu depuis Vercel, préférer la chaîne
> *pooler* de Neon (celle qui contient `-pooler.`) pour éviter de saturer
> les connexions Postgres depuis un environnement serverless. Le
> pipeline, lui, reste sur la chaîne directe (un seul run séquentiel).

## Suivi incrémental

- `cache_hackathons.json` — dernière collecte brute (permet `reclass`
  sans réseau).
- `annonces_vues.json` — historique `(1re détection, dernière vérif,
  verdict)` par événement. Un événement qui disparaît d'une source reste
  tracé ici.

## Automatisation cloud (GitHub Actions)

Ce projet est un **dépôt Git autonome** (pas mélangé au monorepo
`sourcing/`). Remote : https://github.com/niangmamath/hackathon.

Workflow actif :
[`.github/workflows/scrape_hackathons.yml`](.github/workflows/scrape_hackathons.yml).

- Déclenché **tous les jours à 05:23 UTC** (≈ 06h20 heure Maroc) via le
  `schedule: cron: "23 5 * * *"` natif de GitHub Actions. Minute décalée
  du début d'heure : les crons à HH:00 sont les plus retardés par GitHub.
- Déclenchement manuel aussi disponible (`workflow_dispatch`, bouton
  *Run workflow* dans l'onglet Actions).
- Un seul secret requis côté dépôt : `DATABASE_URL` (Neon, port 5432,
  `?sslmode=require`) à ajouter dans Settings → Secrets and variables
  → Actions.
- Cache `cache_hackathons.json` + `annonces_vues.json` préservé entre
  runs (`actions/cache`), de sorte que `premiere_detection` reste
  stable même sans base montée.

Pourquoi `schedule` natif ici (et pas Vercel Cron comme pour
`sourcing-stages-maroc`) : il n'y a pas encore de site Next.js côté
hackathons, et un retard best-effort de quelques minutes/heures est
sans conséquence sur une veille quotidienne (les hackathons ont
des fenêtres de plusieurs jours à plusieurs semaines).

## Tests

```bash
python -m unittest test_classifier
```

Les tests couvrent la détection (titres forts/faibles, formations
exclues, meetups exclus), la géo (en ligne jamais hors Maroc), le calcul
de fenêtre, la déduplication inter-sources et le tri final.

## Limites connues

- **Pas de date fiable sur certains collecteurs** : Eventbrite et MLH
  exposent les dates dans leur JSON-LD / DOM, mais des sources ajoutées
  plus tard peuvent ne pas le faire — ces événements tomberont en
  `INCONNUE` et ne seront pas écartés automatiquement (choix assumé :
  mieux vaut remonter un doute que supprimer).
- **Classification par mots-clés uniquement** (pas de LLM en v1) : un
  événement intitulé "Challenge" sans aucun mot évoquant la compétition
  passe en ÉCARTÉE — revue manuelle recommandée si vous soupçonnez un
  manque.
- **Pas de LinkedIn** : les hackathons y sont souvent relayés via des
  posts, pas via des offres, et le scraping de posts n'est pas supporté
  (voir section Sources).

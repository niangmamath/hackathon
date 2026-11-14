# -*- coding: utf-8 -*-
"""Veille des hackathons au Maroc (+ hackathons en ligne accessibles).

Pipeline :

    collecte multi-sources -> classification -> synchro Postgres (Supabase)

La sortie est une table Postgres `hackathons` lue directement par le site
web, pas un Excel (contrairement à sourcing-regie-banque) : pas
d'annotations manuelles à conserver ici, le reflet "ce qui est convenable
aujourd'hui" est entièrement produit par le pipeline.

Usage :
    python hackathons_maroc.py            # collecte complète (réseau) + DB
    python hackathons_maroc.py reclass    # re-classe depuis le cache local
"""
import datetime as dt
import json
import os
import sys

if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Charge `.env` (DATABASE_URL, etc.) si python-dotenv est installé. Absent
# en CI/GitHub Actions où les variables sont déjà exportées — pas une
# erreur, juste rien à charger.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              ".env"))
except ImportError:
    pass

from classifier import classify_all
import db_sync
import sources


OUTDIR = os.path.dirname(os.path.abspath(__file__))
VUES_FILE = os.path.join(OUTDIR, "annonces_vues.json")
CACHE_FILE = os.path.join(OUTDIR, "cache_hackathons.json")


# ----------------------------------------------------------------- JSON I/O
def _load(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------- SUIVI VUES
def _key(a):
    """Clé stable d'une annonce entre runs — URL si disponible, sinon
    (source, organisateur, titre)."""
    url = (a.get("url") or "").strip()
    if url:
        return url
    return f"{a.get('source','?')}::{a.get('entite','')}::{a.get('poste','')}"


def _update_vues(annonces, today):
    """`annonces_vues.json` conserve (1re détection, dernière vérif, verdict)
    pour chaque événement rencontré, indépendamment de la base — un
    hackathon qui disparaît des sources reste tracé ici."""
    vues = _load(VUES_FILE)
    for a in annonces:
        k = _key(a)
        ent = vues.get(k) or {}
        ent.setdefault("premiere_detection", today)
        ent["derniere_verif"] = today
        ent["verdict"] = a.get("verdict")
        vues[k] = ent
        a["premiere_detection"] = ent["premiere_detection"]
        a["derniere_verif"] = ent["derniere_verif"]
    _save(VUES_FILE, vues)
    return annonces


# ------------------------------------------------------------------- MAIN
def harvest():
    """Collecte réseau : remplit le cache brut."""
    print("Collecte des hackathons...")
    annonces = sources.collect_all()
    print(f"  Total brut : {len(annonces)} annonces")
    _save(CACHE_FILE,
           {"annonces": annonces,
            "collecte": dt.datetime.now().isoformat(timespec="seconds")})
    return annonces


def run(mode="full"):
    today = dt.date.today().isoformat()
    if mode == "reclass":
        cache = _load(CACHE_FILE)
        annonces = cache.get("annonces") or []
        print(f"Rechargé {len(annonces)} annonces depuis le cache.")
    else:
        annonces = harvest()

    classes = classify_all(annonces, today)
    classes = _update_vues(classes, today)

    convenables = [a for a in classes if a["verdict"] == "CONVENABLE"]
    ecartees = [a for a in classes if a["verdict"] == "ÉCARTÉE"]
    print(f"  Classés    : {len(classes)} ({len(convenables)} convenables, "
          f"{len(ecartees)} écartés)")

    db_sync.sync(classes)
    return classes


if __name__ == "__main__":
    mode = "reclass" if len(sys.argv) > 1 and sys.argv[1] == "reclass" else "full"
    run(mode)

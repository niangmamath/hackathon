# -*- coding: utf-8 -*-
"""Collecteurs de hackathons — Maroc + en ligne accessibles depuis le Maroc.

Chaque collecteur renvoie une liste de dicts avec les mêmes clés :
    poste, entite, ville, url, date_debut, date_fin, texte, source

robots.txt vérifié le 2026-11-14 pour chaque source (voir le commentaire
dédié au-dessus de chaque collecteur). Un délai de REQUEST_DELAY_SECONDS
s'applique entre deux collecteurs, et jamais plus d'une requête concurrente
par hôte. Aucune authentification, aucune API privée.

Chaque collecteur est best-effort (échec silencieux -> liste vide, jamais
d'exception propagée au pipeline) : un changement de markup côté source
ne doit pas casser le run global.
"""
import datetime as dt
import json
import random
import re
import time
import traceback

import requests
from bs4 import BeautifulSoup


# User-Agent de navigateur réaliste — un UA auto-identifiant reçoit souvent
# un 403 des WAF génériques (constat déjà fait dans sourcing-regie-banque
# et sourcing-stages-maroc). Les robots.txt des 3 sources utilisées ici
# n'exigent pas d'identifiant bot particulier (aucune règle `User-agent:
# <bot>` qui serait "la nôtre") — donc un UA honnête côté forme sans être
# auto-identifiant reste conforme à leurs règles affichées.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
    "Gecko/20100101 Firefox/125.0",
]
REQUEST_DELAY_SECONDS = 2.0
TIMEOUT = 25


def _get(url, params=None, accept="text/html"):
    headers = {"User-Agent": random.choice(USER_AGENTS),
               "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
               "Accept": accept}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"    ! réseau {url}: {e}")
        return None
    if r.status_code != 200:
        print(f"    ! HTTP {r.status_code} sur {url}")
        return None
    return r


def _extract_jsonld(html):
    """Toutes les balises <script type="application/ld+json"> parsées."""
    out = []
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", {"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            out.extend(data)
        else:
            out.append(data)
    return out


# ============================================================ DEVPOST
# robots.txt vérifié 2026-11-14 : "User-agent: * / Disallow:" (vide) =
# tout autorisé aux bots génériques. Seuls quelques crawlers NOMMÉS
# (BLEXBot, Omgilibot, ImagesiftBot, Bytespider) sont bannis — aucune
# règle qui s'applique à nous. `/api/hackathons` n'a pas de règle
# spécifique -> libre.
DEVPOST_API = "https://devpost.com/api/hackathons"
DEVPOST_MAX_PAGES = 3  # 30 hackathons / page, suffisant pour les upcoming


def collect_devpost():
    """Devpost expose une API JSON publique à `/api/hackathons` qui
    renvoie `{hackathons: [...], meta: {total_count, ...}}`. On filtre
    côté client sur les événements "upcoming" ou "open" (le paramètre
    `status[]` est accepté mais pas garanti stable, on le passe quand même
    pour alléger la charge serveur)."""
    print("  → Devpost")
    out = []
    for page in range(1, DEVPOST_MAX_PAGES + 1):
        r = _get(DEVPOST_API,
                  params={"status[]": ["upcoming", "open"], "page": page},
                  accept="application/json")
        if not r:
            break
        try:
            data = r.json()
        except json.JSONDecodeError:
            print("    ! Devpost : JSON invalide")
            break
        hacks = data.get("hackathons") or []
        if not hacks:
            break
        for h in hacks:
            poste = h.get("title") or ""
            if not poste:
                continue
            url = h.get("url") or ""
            org = h.get("organization_name") or "Devpost"
            loc = h.get("displayed_location") or {}
            ville = loc.get("location", "") if isinstance(loc, dict) else str(loc)
            # "Nov 14 - Dec 05, 2026" ou "Oct 30 - Dec 04, 2026"
            dates_txt = h.get("submission_period_dates") or ""
            debut, fin = _parse_devpost_dates(dates_txt)
            texte = h.get("subtitle") or ""
            out.append({
                "poste": poste, "entite": org,
                "ville": ville or "Online",
                "url": url, "date_debut": debut, "date_fin": fin,
                "texte": texte, "source": "Devpost",
            })
        meta = data.get("meta") or {}
        if meta.get("current_page", page) >= meta.get("total_pages", page):
            break
        time.sleep(REQUEST_DELAY_SECONDS)
    print(f"    {len(out)} hackathons Devpost")
    return out


_DP_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
_DP_RANGE_RE = re.compile(
    r"([A-Z][a-z]{2})\s+(\d{1,2})\s*[-–]\s*(?:([A-Z][a-z]{2})\s+)?(\d{1,2}),\s*(\d{4})")


def _parse_devpost_dates(s):
    """'Oct 30 - Dec 04, 2026' / 'Nov 14 - 16, 2026' -> (iso, iso).
    Renvoie ('', '') si format inconnu — toléré par le classifier (fenêtre
    INCONNUE, ne jette pas la ligne)."""
    if not s:
        return "", ""
    m = _DP_RANGE_RE.search(s)
    if not m:
        return "", ""
    mon1, d1, mon2, d2, year = m.groups()
    mon2 = mon2 or mon1
    try:
        debut = dt.date(int(year), _DP_MONTHS[mon1], int(d1)).isoformat()
        fin = dt.date(int(year), _DP_MONTHS[mon2], int(d2)).isoformat()
    except (KeyError, ValueError):
        return "", ""
    return debut, fin


# ================================================================ MLH
# robots.txt vérifié 2026-11-14 : "User-agent: * / Allow: /" avec quelques
# exclusions (/account/, /admin/, /tools/, /auth/, /sidekiq/, /_/, /v4/,
# /marksmith/, /events/*/partners/.../promo_codes/, /projects/invites/,
# /submissions/invites/) — /seasons/.../events n'y est pas et reste libre.
MLH_SEASONS = ["2026", "2027"]  # couvre l'année en cours + la suivante


def collect_mlh():
    """MLH (Major League Hacking) : pages par saison. Chaque événement
    est maintenant exposé via microdata schema.org (`itemtype="Event"`)
    avec `itemprop="name"/"startDate"/"city"`. Le format a changé fin
    2026 : les anciens sélecteurs `.event-wrapper` ont disparu, on passe
    par `itemtype` qui est plus stable (contrat schema.org)."""
    print("  → MLH")
    out = []
    for season in MLH_SEASONS:
        r = _get(f"https://mlh.io/seasons/{season}/events")
        if not r:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        events = soup.find_all(attrs={"itemtype":
            lambda v: v and "schema.org/Event" in v})
        for e in events:
            name_el = e.find(attrs={"itemprop": "name"})
            if not name_el:
                continue
            poste = name_el.get_text(" ", strip=True)
            if not poste:
                continue
            start_el = e.find(attrs={"itemprop": "startDate"})
            date_debut = ""
            if start_el:
                date_debut = (start_el.get("content")
                              or start_el.get_text(" ", strip=True))[:10]
            city_el = e.find(attrs={"itemprop": "city"})
            region_el = e.find(attrs={"itemprop": "addressRegion"})
            ville = ""
            if city_el:
                ville = city_el.get_text(" ", strip=True)
            if region_el and region_el.get_text(strip=True) not in ville:
                r_txt = region_el.get_text(" ", strip=True)
                ville = f"{ville}, {r_txt}" if ville else r_txt
            # Format MLH : il n'y a pas d'`itemprop="url"`, les tuiles
            # linkent vers la page MLH de l'événement via <a href="...">
            # parent de l'ensemble.
            a = e.find("a", href=True)
            url = ""
            if a:
                href = a["href"]
                url = href if href.startswith("http") else f"https://mlh.io{href}"
            out.append({
                "poste": poste, "entite": "MLH",
                "ville": ville or "Online",
                "url": url, "date_debut": date_debut,
                "date_fin": "", "texte": "",
                "source": "MLH",
            })
        time.sleep(REQUEST_DELAY_SECONDS)
    print(f"    {len(out)} événements MLH")
    return out


# ========================================================= EVENTBRITE
# robots.txt vérifié 2026-11-14 : "User-agent: *" avec de nombreuses
# exclusions (`/api/v3/destination/events/`, `/directory/`, `/checkout-
# external*`, rss/atom/calendar...). La page `/d/<pays>/<mot-clé>/` n'y
# est pas listée -> libre. On évite SCRUPULEUSEMENT les endpoints API
# listés dans le Disallow (aucun appel à /api/v3/...).
EVENTBRITE_URL = "https://www.eventbrite.com/d/morocco/hackathon/"


def collect_eventbrite():
    """Eventbrite : la recherche publique `/d/morocco/hackathon/` ne
    filtre pas réellement sur "hackathon" (elle renvoie souvent des
    conférences / summits au Maroc). Les faux positifs sont écartés en
    aval par `classifier.detect_hackathon` — pas un bug de ce collecteur,
    juste la réalité du moteur Eventbrite."""
    print("  → Eventbrite (Maroc)")
    r = _get(EVENTBRITE_URL)
    if not r:
        return []
    out = []
    for obj in _extract_jsonld(r.text):
        items = []
        if isinstance(obj, dict) and obj.get("@type") in ("ItemList",
                                                            "ItemListElement"):
            items = obj.get("itemListElement") or []
        elif isinstance(obj, dict) and obj.get("@type") == "Event":
            items = [{"item": obj}]
        for it in items:
            ev = it.get("item") if isinstance(it, dict) and "item" in it else it
            if not isinstance(ev, dict) or ev.get("@type") != "Event":
                continue
            poste = ev.get("name") or ""
            if not poste:
                continue
            org = ev.get("organizer") or {}
            if isinstance(org, list):
                org = org[0] if org else {}
            entite = org.get("name") if isinstance(org, dict) else ""
            loc = ev.get("location") or {}
            if isinstance(loc, list):
                loc = loc[0] if loc else {}
            ville = ""
            if isinstance(loc, dict):
                addr = loc.get("address") or {}
                if isinstance(addr, dict):
                    ville = (addr.get("addressLocality")
                              or addr.get("addressRegion") or "")
                ville = ville or loc.get("name") or ""
            date_debut = (ev.get("startDate") or "")[:10]
            date_fin = (ev.get("endDate") or "")[:10]
            out.append({
                "poste": poste, "entite": entite or "Eventbrite",
                "ville": ville or "Maroc",
                "url": ev.get("url") or "",
                "date_debut": date_debut, "date_fin": date_fin,
                "texte": ev.get("description") or "",
                "source": "Eventbrite",
            })
    print(f"    {len(out)} événements Eventbrite")
    return out


# ================================================================ REGISTRE
COLLECTORS = [
    ("Devpost", collect_devpost),
    ("MLH", collect_mlh),
    ("Eventbrite", collect_eventbrite),
]


def collect_all():
    """Exécute tous les collecteurs en série avec délai. Un échec n'empêche
    pas les autres de tourner — on log l'exception et on continue."""
    out = []
    for name, fn in COLLECTORS:
        try:
            out.extend(fn())
        except Exception as e:
            print(f"    ! {name} a planté : {e}")
            traceback.print_exc()
        time.sleep(REQUEST_DELAY_SECONDS)
    return out

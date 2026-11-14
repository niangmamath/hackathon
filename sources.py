# -*- coding: utf-8 -*-
"""Collecteurs de hackathons — Maroc + en ligne accessibles depuis le Maroc.

Chaque collecteur renvoie une liste de dicts avec les mêmes clés :
    poste, entite, ville, url, date_debut, date_fin, texte, source

robots.txt vérifié le 2026-11-14 pour chaque source (voir le commentaire
dédié au-dessus de chaque collecteur). Un délai de REQUEST_DELAY_SECONDS
s'applique entre deux collecteurs. Aucune authentification, aucune API
privée.

Chaque collecteur est best-effort (échec silencieux -> liste vide, jamais
d'exception propagée au pipeline) : un changement de markup côté source
ne doit pas casser le run global.

Note sur Eventbrite (retiré) : la recherche publique `/d/morocco/hackathon/`
ne filtre pas réellement sur le mot-clé, elle renvoyait des conférences /
summits / meetups marocains (Odoo Business Show, Leadership Summit, chess
networking...) écartés à 100 % en aval. En plus, Eventbrite répond 405
depuis les IP cloud (GitHub Actions) — bruit pur sans aucun gain.
"""
import datetime as dt
import json
import random
import re
import time
import traceback

import requests
from bs4 import BeautifulSoup


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


# ============================================================ DEVPOST
# robots.txt vérifié 2026-11-14 : "User-agent: * / Disallow:" (vide) =
# tout autorisé aux bots génériques. `/api/hackathons` libre.
DEVPOST_API = "https://devpost.com/api/hackathons"
DEVPOST_MAX_PAGES = 3


def collect_devpost():
    """Devpost expose une API JSON publique à `/api/hackathons` qui
    renvoie `{hackathons: [...], meta: {total_count, ...}}`."""
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
            dates_txt = h.get("submission_period_dates") or ""
            debut, fin = _parse_devpost_dates(dates_txt)
            texte = h.get("subtitle") or ""
            out.append({
                "poste": poste, "entite": org,
                "ville": ville or "Online",
                "url": url, "date_debut": debut, "date_fin": fin,
                "texte": texte, "source": "Devpost",
                # Devpost = catalogue 100 % hackathons par construction :
                # on dit explicitement au classifieur qu'il n'a pas besoin
                # de re-prouver que c'en est un (évite les faux rejets
                # comme "Codegeist" / "Kiroween" qui n'ont pas le mot
                # "hackathon" dans le titre).
                "est_hackathon_force": True,
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
    """'Oct 30 - Dec 04, 2026' / 'Nov 14 - 16, 2026' -> (iso, iso)."""
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
# exclusions (/account/, /admin/, /tools/, ...). /seasons/.../events libre.
#
# Même logique que Devpost : MLH est un catalogue 100 % hackathons
# étudiants, pas besoin de re-prouver via mots-clés (les titres style
# "Quackhacks 3" / "HackCMU" / "HopHacks" ne contiennent pas forcément
# "hackathon" littéralement).
MLH_SEASONS = ["2026", "2027"]


def collect_mlh():
    """MLH (Major League Hacking) : pages par saison. Markup récent :
    chaque événement est un `<a itemtype="schema.org/Event">` contenant
    un `<h4>` avec le vrai nom de l'événement (ex. "Quackhacks 3"),
    un `<meta itemprop="startDate">`, un `<meta itemprop="endDate">`,
    une `<div itemprop="location">` avec `<meta itemprop="addressLocality">`
    et `<meta itemprop="addressCountry">`, et un `<meta itemprop=
    "eventAttendanceMode">` qui dit "Online" / "Offline" / "Mixed".

    Les versions antérieures du scraper utilisaient `itemprop="name"` qui
    était sur la LOCATION (nom de la ville), ce qui faisait remonter
    "Arlington, Texas" comme titre d'événement."""
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
            # Titre : <h4> dans la carte (le seul heading dans cet
            # élément).
            h = e.find(["h1", "h2", "h3", "h4", "h5", "h6"])
            poste = h.get_text(" ", strip=True) if h else ""
            if not poste:
                continue
            start = e.find("meta", itemprop="startDate")
            end = e.find("meta", itemprop="endDate")
            date_debut = (start.get("content") if start else "")[:10]
            date_fin = (end.get("content") if end else "")[:10]
            # Lieu : la location est une sous-balise avec son propre
            # itemprop="addressLocality" / "addressCountry".
            locality = e.find("meta", itemprop="addressLocality")
            country = e.find("meta", itemprop="addressCountry")
            ville = locality.get("content") if locality else ""
            if country and country.get("content"):
                ville = f"{ville}, {country.get('content')}" if ville else country.get("content")
            # Mode : OnlineEventAttendanceMode / OfflineEventAttendanceMode /
            # MixedEventAttendanceMode.
            mode = e.find("meta", itemprop="eventAttendanceMode")
            mode_txt = (mode.get("content") if mode else "") or ""
            en_ligne = "Online" in mode_txt or "Mixed" in mode_txt
            # Si en ligne, on force "Online" côté ville pour que le
            # classifieur garde l'événement même si l'org est hors Maroc.
            if en_ligne:
                ville = "Online"
            # URL : l'événement est lui-même un <a href="...">.
            url = e.get("href", "")
            if not url and e.name != "a":
                a = e.find("a", href=True)
                url = a["href"] if a else ""
            out.append({
                "poste": poste, "entite": "MLH",
                "ville": ville, "url": url,
                "date_debut": date_debut, "date_fin": date_fin,
                "texte": "", "source": "MLH",
                "est_hackathon_force": True,
            })
        time.sleep(REQUEST_DELAY_SECONDS)
    print(f"    {len(out)} événements MLH")
    return out


# ================================================================ REGISTRE
# Eventbrite retiré (cf. docstring du module).
COLLECTORS = [
    ("Devpost", collect_devpost),
    ("MLH", collect_mlh),
]


def collect_all():
    out = []
    for name, fn in COLLECTORS:
        try:
            out.extend(fn())
        except Exception as e:
            print(f"    ! {name} a planté : {e}")
            traceback.print_exc()
        time.sleep(REQUEST_DELAY_SECONDS)
    return out

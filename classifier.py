# -*- coding: utf-8 -*-
"""Classification des HACKATHONS pertinents pour le Maroc.

Projet frère de sourcing-stages-maroc : même architecture (détecteurs purs,
composés par verdict_of, dédup inter-sources, tag de domaine informatif),
mais trois différences de fond :

1. L'objet détecté n'est pas un contrat (stage / CDI) mais un événement
   ponctuel (hackathon, datathon, ideathon, coding challenge, game jam...).
2. La fraîcheur ne se calcule PAS par rapport à la date d'ANNONCE : un
   hackathon publié il y a 3 mois mais qui a lieu la semaine prochaine est
   encore d'actualité. On prend donc la date de l'ÉVÉNEMENT (début) comme
   référence quand elle est disponible.
3. Un hackathon "en ligne / online" accessible depuis le Maroc reste dans
   le périmètre, même si son organisateur est hors Maroc. Un hackathon
   présentiel ailleurs (Paris, Dubaï...) est écarté.
"""
import datetime as dt
import re
import unicodedata


# --------------------------------------------------------------- TEXTE UTILS
def strip_accents(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))


def _strip_invisibles(s):
    return "".join(c for c in (s or "")
                   if unicodedata.category(c) not in ("Cf", "Cc") or c in "\n\t")


def _pad(s):
    return " " + (s or "").lower() + " "


def has_any(text, kws):
    t = _pad(text)
    return any(k in t for k in kws)


def normalize_title(title):
    t = strip_accents(title).lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"\b(hackathon|hack|challenge|competition|edition|20\d{2})\b",
               " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def dedup_annonces(annonces):
    """Fusionne les doublons inter-sources — même organisateur + titre
    normalisé. Conserve la première occurrence."""
    seen, out = set(), []
    for a in annonces:
        key = (strip_accents(a.get("entite", "")).lower().strip(),
               normalize_title(a.get("poste", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


# ------------------------------------------------------------- DETECTION
# Mots-clés haute précision dans le titre : s'il y a "hackathon" dans le
# titre, c'est quasi certainement un hackathon (très peu de faux positifs).
HACKATHON_TITLE_KW = [
    "hackathon", "hack-a-thon", "hack a thon",
    "datathon", "ideathon", "makeathon", "designathon", "gamejam",
    "game jam", "codejam", "code jam", "coding challenge",
    "coding competition", "programming contest", "cp contest",
    "ctf", "capture the flag",
]

# Mots-clés plus faibles — doivent apparaître avec un signal de compétition
# organisée pour confirmer (évite de tagger comme hackathon un simple cours
# "coding bootcamp" ou un meetup "coding night").
HACKATHON_WEAK_KW = [
    "innovation challenge", "startup weekend", "challenge innovation",
    "concours d'innovation", "concours innovation",
    "coding marathon", "marathon de code", "marathon de programmation",
    "appel à projets tech", "concours de developpeurs",
    "concours de développeurs",
]
HACKATHON_CONFIRM_KW = [
    "equipe", "équipe", "team", "pitch", "jury", "prix", "prize",
    "award", "cash prize", "winners", "lauréats", "laureats", "48h", "72h",
    "24h", "48 heures", "72 heures", "weekend", "week-end", "sprint",
    "submission", "soumission", "projet", "project",
]

# Garde-fou : des formations / bootcamps / meetups qui ne sont PAS des
# hackathons, même s'ils citent "hack" ou "code" dans le texte.
NON_HACKATHON_KW = [
    "bootcamp", "boot camp", "formation certifiante", "cours en ligne",
    "online course", "mooc", "webinar", "webinaire", "conférence",
    "conference", "meetup", "atelier de formation", "workshop recruiting",
    "job fair", "forum de recrutement", "salon de l'emploi",
]


def detect_hackathon(poste, texte):
    """(est_hackathon: bool, motif: str).

    Priorités :
      1. Titre contient un mot-clé fort -> hackathon, sauf si le texte
         indique clairement un format non-compétition (formation, meetup).
      2. Mot-clé faible dans titre/texte + au moins un signal de compétition
         organisée dans le texte -> hackathon.
      3. Sinon pas un hackathon.
    """
    poste_n = _strip_invisibles(poste).lower()
    texte_n = _strip_invisibles(texte or "").lower()
    blob = f" {poste_n} . {texte_n} "

    titre_fort = any(k in _pad(poste_n) for k in HACKATHON_TITLE_KW)
    if titre_fort:
        # Garde-fou exceptionnel : on ne requalifie PAS en hackathon un
        # titre qui est manifestement une formation payante / un cours.
        if any(k in blob for k in NON_HACKATHON_KW) and \
           not any(k in blob for k in ("prize", "prix", "jury", "pitch")):
            return False, "format non-compétition (formation / meetup)"
        return True, ""

    faible_titre = any(k in _pad(poste_n) for k in HACKATHON_WEAK_KW)
    faible_texte = any(k in blob for k in HACKATHON_WEAK_KW)
    if faible_titre or faible_texte:
        if any(k in blob for k in HACKATHON_CONFIRM_KW):
            return True, ""
        return False, "signal faible sans confirmation de compétition"

    # Dernier essai : "hackathon" / "datathon" cités dans le CORPS (pas le
    # titre), fréquent sur les pages d'agrégateurs qui listent un événement
    # parmi d'autres.
    if any(k in blob for k in HACKATHON_TITLE_KW):
        if any(k in blob for k in HACKATHON_CONFIRM_KW):
            return True, ""

    return False, "pas de signal de hackathon"


# ------------------------------------------------------------- GEO + MODE
# Marqueurs explicitement HORS Maroc (ville ou pays). On ne les applique
# QUE si l'événement n'est pas déclaré "en ligne" : un hackathon "online"
# organisé depuis Paris reste dans le périmètre.
GEO_HORS_MAROC_KW = [
    "paris", "lyon", "marseille", "toulouse", "bordeaux", "nantes",
    "lille", "strasbourg", "nice", "france",
    "dubai", "abu dhabi", "doha", "riyadh", "riyad",
    "london", "londres", "madrid", "barcelona", "barcelone",
    "berlin", "munich", "amsterdam", "bruxelles", "brussels",
    "new york", "san francisco", "boston", "toronto", "montreal", "montréal",
    "abidjan", "dakar", "tunis", "tunisie", "alger", "algérie", "algerie",
    "sénégal", "senegal", "côte d'ivoire", "cote d'ivoire",
]

ONLINE_KW = [
    "online", "en ligne", "virtual", "virtuel", "remote",
    "à distance", "a distance", "worldwide", "mondial",
    "global hackathon", "open to all", "ouvert à tous",
]


def is_online(poste, ville, texte=""):
    blob = strip_accents(f"{poste} {ville} {texte}").lower()
    return any(k in blob for k in [strip_accents(k) for k in ONLINE_KW])


def hors_maroc(poste, ville, texte=""):
    """Un événement physique hors Maroc = écarté ; un événement en ligne
    n'est jamais écarté sur ce critère."""
    if is_online(poste, ville, texte):
        return False
    blob = strip_accents(f"{poste} {ville}").lower()
    if "maroc" in blob or "morocco" in blob:
        return False
    return any(k in blob for k in [strip_accents(k) for k in GEO_HORS_MAROC_KW])


# Normalisation ville — reprise de sourcing-stages-maroc. Pour les
# hackathons en ligne, on remplace par "En ligne" pour un tri clair côté
# Excel.
VILLES_CONNUES = [
    ("Casablanca", ["casablanca"]),
    ("Rabat", ["rabat"]),
    ("Marrakech", ["marrakech"]),
    ("Tanger", ["tanger", "tangier"]),
    ("Fès", ["fes", "fès"]),
    ("Agadir", ["agadir"]),
    ("Meknès", ["meknes", "meknès"]),
    ("Oujda", ["oujda"]),
    ("Kénitra", ["kenitra", "kénitra"]),
    ("Tétouan", ["tetouan", "tétouan"]),
    ("Benguerir", ["benguerir", "ben guerir"]),
    ("El Jadida", ["el jadida"]),
    ("Ifrane", ["ifrane"]),
]


def normalize_ville(ville, poste="", texte=""):
    if is_online(poste, ville, texte):
        return "En ligne"
    if not ville or not ville.strip():
        return "Maroc (non précisé)"
    v_full = strip_accents(ville).lower()
    premier = ville.split(",")[0].strip()
    premier_l = strip_accents(premier).lower()
    for canon, variantes in VILLES_CONNUES:
        if any(v in premier_l for v in variantes):
            return canon
    for canon, variantes in VILLES_CONNUES:
        if any(v in v_full for v in variantes):
            return canon
    if "maroc" in v_full or "morocco" in v_full:
        return "Maroc (non précisé)"
    return premier or "Maroc (non précisé)"


# ------------------------------------------------------------------ DOMAINES
# Tags INFORMATIFS, jamais excluants — comme dans sourcing-stages-maroc.
DOMAINE_KW = {
    "IA / Data": [
        "ia", "intelligence artificielle", "artificial intelligence",
        "machine learning", "deep learning", "nlp", "llm", "genai",
        "generative ai", "data", "datathon", "kaggle",
    ],
    "Fintech / Banque": [
        "fintech", "finance", "bancaire", "banque", "paiement", "payment",
        "blockchain", "crypto", "web3", "defi",
    ],
    "Cybersécurité": [
        "cyber", "cybersecurite", "cybersécurité", "cybersecurity",
        "security", "ctf", "capture the flag", "ethical hacking",
        "pentest",
    ],
    "Santé / HealthTech": [
        "health", "sante", "santé", "medical", "médical", "medtech",
        "healthtech", "biotech",
    ],
    "GreenTech / Sustainability": [
        "climate", "climat", "green", "sustainability", "durabilit",
        "énergie", "energie", "environnement", "environment",
    ],
    "EdTech": [
        "edtech", "education", "éducation", "learning",
    ],
    "Mobilité / SmartCity": [
        "mobility", "mobilité", "smart city", "ville intelligente",
        "transport",
    ],
    "GovTech / Impact": [
        "govtech", "civic", "social impact", "impact social",
        "humanitaire", "ngo", "ong",
    ],
}
_DOMAINE_RE = {
    label: [re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)")
            for k in kws]
    for label, kws in DOMAINE_KW.items()
}


def tag_domaine(poste, texte):
    blob = f" {strip_accents(poste).lower()} {strip_accents(texte).lower()} "
    scores = {}
    for label, regs in _DOMAINE_RE.items():
        n = sum(len(r.findall(blob)) for r in regs)
        if n:
            scores[label] = n
    if not scores:
        return "Généraliste"
    return max(scores, key=scores.get)


# -------------------------------------------------------------------- DATES
def _parse_iso(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except (ValueError, TypeError):
        return None


def fenetre_from_event(date_debut_iso, date_fin_iso, today):
    """Fraîcheur calculée sur la date d'ÉVÉNEMENT (début de préférence,
    fin à défaut). Ce n'est PAS l'âge de l'annonce.

      - PASSÉ    : la date de fin est révolue  -> l'événement est écarté
      - EN COURS : aujourd'hui dans [début, fin]
      - IMMINENT : début ≤ aujourd'hui + 7 j
      - BIENTÔT  : début ≤ aujourd'hui + 30 j
      - ANNONCÉ  : début > aujourd'hui + 30 j
      - INCONNUE : pas de date utilisable -> on ne jette rien, on remonte
                    simplement l'incertitude.
    """
    td = dt.date.fromisoformat(today) if isinstance(today, str) else today
    d = _parse_iso(date_debut_iso)
    f = _parse_iso(date_fin_iso) or d
    if d is None and f is None:
        return "INCONNUE"
    # Si on n'a que la fin, on l'utilise comme pivot bas aussi.
    debut = d or f
    fin = f or d
    if fin < td:
        return "PASSÉ"
    if debut <= td <= fin:
        return "EN COURS"
    delta = (debut - td).days
    if delta <= 7:
        return "IMMINENT"
    if delta <= 30:
        return "BIENTÔT"
    return "ANNONCÉ"


# ------------------------------------------------------------------ VERDICT
def verdict_of(a):
    """(verdict, motif). CONVENABLE ou ÉCARTÉE."""
    if not a.get("est_hackathon"):
        return "ÉCARTÉE", a.get("motif_hackathon") or "pas un hackathon"
    if a.get("hors_maroc_flag"):
        return "ÉCARTÉE", "hors Maroc et pas en ligne"
    if a.get("fenetre") == "PASSÉ":
        return "ÉCARTÉE", "événement passé"
    return "CONVENABLE", ""


def classifier(annonce, today=None):
    today = today or dt.date.today().isoformat()
    poste = _strip_invisibles(annonce.get("poste", ""))
    texte = _strip_invisibles(annonce.get("texte", "") or "")
    entite = _strip_invisibles(annonce.get("entite", ""))
    ville = annonce.get("ville", "") or annonce.get("lieu", "")

    est, motif = detect_hackathon(poste, texte)
    online = is_online(poste, ville, texte)
    hm = hors_maroc(poste, ville, texte)
    domaine = tag_domaine(poste, texte)
    fen = fenetre_from_event(annonce.get("date_debut"),
                              annonce.get("date_fin"), today)

    out = dict(annonce)
    out.update({
        "poste": poste, "texte": texte, "entite": entite,
        "est_hackathon": est, "motif_hackathon": motif,
        "en_ligne": online, "hors_maroc_flag": hm,
        "domaine": domaine, "fenetre": fen,
        "ville": normalize_ville(ville, poste, texte),
    })
    verdict, motif_v = verdict_of(out)
    out["verdict"] = verdict
    out["motif"] = motif_v
    return out


# Ordre de tri Excel : CONVENABLES d'abord, puis par imminence croissante
# (EN COURS, IMMINENT, BIENTÔT, ANNONCÉ, INCONNUE, puis les écartées).
_ORDRE_FENETRE = {
    "EN COURS": 0, "IMMINENT": 1, "BIENTÔT": 2,
    "ANNONCÉ": 3, "INCONNUE": 4, "PASSÉ": 5,
}


def classify_all(annonces, today=None):
    today = today or dt.date.today().isoformat()
    items = [classifier(a, today) for a in dedup_annonces(annonces)]
    items.sort(key=lambda a: (
        0 if a["verdict"] == "CONVENABLE" else 1,
        _ORDRE_FENETRE.get(a.get("fenetre", ""), 9),
        a.get("date_debut") or "9999-99-99",
    ))
    return items

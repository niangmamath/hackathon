# -*- coding: utf-8 -*-
"""Tests unitaires du classifieur hackathons — pur, hors réseau.

    python -m unittest test_classifier
"""
import datetime as dt
import unittest

from classifier import (
    detect_hackathon, is_online, hors_maroc, normalize_ville,
    fenetre_from_event, tag_domaine, verdict_of, classifier, classify_all,
    dedup_annonces,
)


TODAY = "2026-11-14"


def _hk(**kw):
    """Fabrique minimale d'une annonce de test."""
    d = {"poste": "", "entite": "", "ville": "", "texte": "", "url": "",
         "date_debut": "", "date_fin": "", "source": "Test"}
    d.update(kw)
    return d


class TestDetection(unittest.TestCase):
    def test_hackathon_titre_fort(self):
        ok, _ = detect_hackathon("Hackathon IA 2026", "")
        self.assertTrue(ok)

    def test_datathon_titre(self):
        ok, _ = detect_hackathon("Datathon Rabat", "")
        self.assertTrue(ok)

    def test_ctf_titre(self):
        ok, _ = detect_hackathon("Casablanca CTF — Capture the Flag", "")
        self.assertTrue(ok)

    def test_signal_faible_sans_confirmation(self):
        ok, motif = detect_hackathon("Innovation Challenge",
                                       "Appel à candidatures ouvert")
        self.assertFalse(ok)
        self.assertIn("confirmation", motif)

    def test_signal_faible_avec_confirmation(self):
        ok, _ = detect_hackathon(
            "Innovation Challenge",
            "48h pour pitcher votre projet devant le jury, prix de 10 000 MAD")
        self.assertTrue(ok)

    def test_formation_pas_hackathon(self):
        # Même avec "hackathon" dans le titre, un bootcamp/formation sans
        # aucun signal de compétition (pas de jury, pas de prix) est écarté.
        ok, motif = detect_hackathon(
            "Hackathon Bootcamp",
            "formation certifiante en ligne")
        self.assertFalse(ok)
        self.assertIn("formation", motif)

    def test_meetup_pas_hackathon(self):
        ok, _ = detect_hackathon("Meetup Python Rabat", "")
        self.assertFalse(ok)


class TestGeo(unittest.TestCase):
    def test_en_ligne_pas_hors_maroc(self):
        self.assertFalse(hors_maroc("Hackathon IA", "Paris", "100% online"))
        self.assertTrue(is_online("Hackathon IA", "Paris", "100% online"))

    def test_physique_hors_maroc(self):
        self.assertTrue(hors_maroc("Hackathon fintech", "Paris", ""))

    def test_maroc_dans_ville(self):
        self.assertFalse(hors_maroc("Hackathon IA", "Casablanca, Maroc", ""))

    def test_normalisation_ville(self):
        self.assertEqual(normalize_ville("Casablanca, Casablanca-Settat, Maroc"),
                          "Casablanca")
        self.assertEqual(normalize_ville("", poste="Hackathon online",
                                           texte="100% online"),
                          "En ligne")
        self.assertEqual(normalize_ville(""), "Maroc (non précisé)")


class TestDomaines(unittest.TestCase):
    def test_tag_data(self):
        self.assertEqual(tag_domaine("AI Datathon", "machine learning"),
                          "IA / Data")

    def test_tag_blockchain(self):
        # Blockchain/Web3 a été sorti de Fintech pour sa propre catégorie
        # (vocabulaire Devpost distinct : "Blockchain", "Cryptocurrency").
        self.assertEqual(tag_domaine("Blockchain hackathon", "web3 DeFi"),
                          "Blockchain / Web3")

    def test_tag_fintech(self):
        self.assertEqual(tag_domaine("Fintech hackathon", "banque paiement"),
                          "Fintech / Banque")

    def test_tag_defaut(self):
        self.assertEqual(tag_domaine("Hackathon général", ""),
                          "Non classé")

    def test_tag_themes_devpost_ai(self):
        # Les thèmes officiels Devpost priment sur les mots-clés : un
        # titre neutre ("Codegeist 2026") mais thème "Machine Learning/AI"
        # doit tomber en "IA / Data".
        self.assertEqual(
            tag_domaine("Codegeist 2026", "",
                         themes=["Machine Learning/AI", "Enterprise"]),
            "IA / Data")

    def test_tag_themes_devpost_gaming(self):
        self.assertEqual(
            tag_domaine("Reddit's Game of the Day", "",
                         themes=["Beginner Friendly", "Gaming"]),
            "Jeu vidéo")

    def test_tag_themes_neutres_ouvert(self):
        # Seuls des thèmes neutres -> "Ouvert" (pas "Non classé").
        self.assertEqual(
            tag_domaine("DSH Hacks V2", "",
                         themes=["Beginner Friendly", "Open Ended"]),
            "Ouvert")


class TestFenetre(unittest.TestCase):
    def test_passe(self):
        self.assertEqual(fenetre_from_event("2026-10-01", "2026-10-03",
                                             TODAY), "PASSÉ")

    def test_en_cours(self):
        self.assertEqual(fenetre_from_event("2026-11-13", "2026-11-15",
                                             TODAY), "EN COURS")

    def test_imminent(self):
        self.assertEqual(fenetre_from_event("2026-11-18", "2026-11-20",
                                             TODAY), "IMMINENT")

    def test_bientot(self):
        self.assertEqual(fenetre_from_event("2026-12-05", "2026-12-07",
                                             TODAY), "BIENTÔT")

    def test_annonce(self):
        self.assertEqual(fenetre_from_event("2027-03-01", "2027-03-03",
                                             TODAY), "ANNONCÉ")

    def test_inconnue(self):
        self.assertEqual(fenetre_from_event("", "", TODAY), "INCONNUE")


class TestVerdict(unittest.TestCase):
    def test_convenable(self):
        a = classifier(_hk(poste="Hackathon IA Rabat",
                            ville="Rabat, Maroc",
                            date_debut="2026-12-10",
                            date_fin="2026-12-12"), TODAY)
        self.assertEqual(a["verdict"], "CONVENABLE")
        self.assertEqual(a["fenetre"], "BIENTÔT")
        self.assertEqual(a["ville"], "Rabat")

    def test_ecartee_passee(self):
        a = classifier(_hk(poste="Hackathon fintech",
                            ville="Casablanca, Maroc",
                            date_debut="2026-09-01",
                            date_fin="2026-09-03"), TODAY)
        self.assertEqual(a["verdict"], "ÉCARTÉE")
        self.assertEqual(a["motif"], "événement passé")

    def test_ecartee_hors_maroc(self):
        a = classifier(_hk(poste="Hackathon fintech",
                            ville="Paris",
                            date_debut="2026-12-10",
                            date_fin="2026-12-12"), TODAY)
        self.assertEqual(a["verdict"], "ÉCARTÉE")
        self.assertIn("hors Maroc", a["motif"])

    def test_online_hors_maroc_conserve(self):
        a = classifier(_hk(poste="Global AI Hackathon",
                            ville="Paris",
                            texte="Open worldwide, 100% online",
                            date_debut="2026-12-10",
                            date_fin="2026-12-12"), TODAY)
        self.assertEqual(a["verdict"], "CONVENABLE")
        self.assertTrue(a["en_ligne"])
        self.assertEqual(a["ville"], "En ligne")

    def test_pas_hackathon(self):
        a = classifier(_hk(poste="Développeur backend CDI",
                            ville="Casablanca, Maroc",
                            date_debut="2026-12-10"), TODAY)
        self.assertEqual(a["verdict"], "ÉCARTÉE")


class TestDedup(unittest.TestCase):
    def test_meme_evenement_deux_sources(self):
        items = [
            _hk(poste="Hackathon AI Maroc 2026", entite="OCP", source="A"),
            _hk(poste="Hackathon AI Maroc 2026", entite="OCP", source="B"),
        ]
        self.assertEqual(len(dedup_annonces(items)), 1)

    def test_organisateurs_differents_pas_dedup(self):
        items = [
            _hk(poste="Hackathon IA", entite="OCP"),
            _hk(poste="Hackathon IA", entite="UM6P"),
        ]
        self.assertEqual(len(dedup_annonces(items)), 2)


class TestClassifyAll(unittest.TestCase):
    def test_tri(self):
        items = [
            _hk(poste="Hackathon futur", ville="Rabat, Maroc",
                date_debut="2027-05-01", date_fin="2027-05-03"),
            _hk(poste="Hackathon imminent", ville="Casablanca, Maroc",
                date_debut="2026-11-17", date_fin="2026-11-19"),
            _hk(poste="Développeur CDI", ville="Casablanca, Maroc"),
        ]
        out = classify_all(items, TODAY)
        self.assertEqual(out[0]["poste"], "Hackathon imminent")
        self.assertEqual(out[1]["poste"], "Hackathon futur")
        self.assertEqual(out[-1]["verdict"], "ÉCARTÉE")


if __name__ == "__main__":
    unittest.main()

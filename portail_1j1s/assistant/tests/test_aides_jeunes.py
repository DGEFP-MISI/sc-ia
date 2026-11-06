"""Tests du connecteur des aides, sans requête réseau."""

from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from portail_1j1s.assistant.services.aides_jeunes import search_aides


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class AidesJeunesTests(SimpleTestCase):
    @patch("portail_1j1s.assistant.services.aides_jeunes.get_catalogue")
    def test_search_filters_private_and_demo(self, catalogue):
        catalogue.return_value = [
            {
                "id": "aide-permis",
                "label": "Aide au permis de conduire",
                "description": "Financement du permis",
                "institution": {"label": "État"},
                "link": "https://example.org/permis",
                "conditions": [],
            },
            {"id": "private", "label": "Aide au permis", "private": True},
            {"id": "aide-demonstration", "label": "Aide au permis"},
        ]
        results = search_aides("Je cherche une aide pour mon permis")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["titre"], "Aide au permis de conduire")

    @patch("portail_1j1s.assistant.services.aides_jeunes.get_catalogue")
    def test_no_match(self, catalogue):
        catalogue.return_value = [{"id": "logement", "label": "Aide au logement"}]
        self.assertEqual(search_aides("permis"), [])

    @patch("portail_1j1s.assistant.services.aides_jeunes.get_catalogue")
    def test_filters_age_and_department(self, catalogue):
        catalogue.return_value = [
            {
                "id": "permis-35",
                "label": "Aide permis",
                "conditions_generales": [
                    {"type": "age", "operator": "<=", "value": 18},
                    {"type": "departements", "values": ["35"]},
                ],
            },
            {
                "id": "permis-51",
                "label": "Aide permis",
                "conditions_generales": [
                    {"type": "age", "operator": ">=", "value": 18},
                    {"type": "departements", "values": ["51"]},
                ],
            },
        ]
        result = search_aides("permis", profile={"age": 20, "departement": "51"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["criteres"][1]["values"], ["51"])

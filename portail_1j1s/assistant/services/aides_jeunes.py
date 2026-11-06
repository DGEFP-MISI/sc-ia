"""Consultation du catalogue public des aides 1jeune1solution.

Ce catalogue fournit des métadonnées, pas une décision d'éligibilité.
"""

import re
import unicodedata
from html import unescape

import requests
from django.core.cache import cache

BENEFITS_URL = "https://mes-aides.1jeune1solution.beta.gouv.fr/api/benefits"
CACHE_KEY = "assistant:aides_jeunes:catalogue:v1"
CACHE_SECONDS = 6 * 60 * 60
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_RESULTS = 6
STOP_WORDS = {
    "a", "ai", "au", "aux", "avec", "comment", "dans", "de", "des", "du",
    "en", "est", "et", "je", "la", "le", "les", "ma", "me", "mes",
    "mon", "pour", "puis", "quelles", "quels", "que", "qui", "sur",
    "une", "un", "veux", "vous",
}


class AidesJeunesAPIError(Exception):
    """Le catalogue des aides est indisponible ou invalide."""


def _normalize(value):
    value = unicodedata.normalize("NFKD", str(value or "").lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _plain_text(value):
    return unescape(re.sub(r"<[^>]+>", " ", str(value or ""))).strip()


def get_catalogue():
    """Récupère le catalogue avec un cache serveur partagé."""
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached
    try:
        response = requests.get(
            BENEFITS_URL,
            timeout=(3, 12),
            headers={"Accept": "application/json"},
            stream=True,
        )
        response.raise_for_status()
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise AidesJeunesAPIError("Catalogue trop volumineux")
            chunks.append(chunk)
        import json

        data = json.loads(b"".join(chunks))
    except (requests.RequestException, ValueError) as exc:
        raise AidesJeunesAPIError("Catalogue indisponible") from exc
    finally:
        if "response" in locals():
            response.close()
    if not isinstance(data, list):
        raise AidesJeunesAPIError("Format du catalogue inattendu")
    cache.set(CACHE_KEY, data, CACHE_SECONDS)
    return data


def search_aides(question, *, limit=MAX_RESULTS):
    """Recherche lexicale prudente, sans conclure à une éligibilité."""
    tokens = set(_normalize(question).split()) - STOP_WORDS
    if not tokens:
        return []
    matches = []
    for aide in get_catalogue():
        if not isinstance(aide, dict) or aide.get("private") is True:
            continue
        if "demonstration" in _normalize(aide.get("id")) or "test" in _normalize(aide.get("id")):
            continue
        label = _normalize(aide.get("label"))
        description = _normalize(_plain_text(aide.get("description")))
        conditions = _normalize(" ".join(map(_plain_text, aide.get("conditions") or [])))
        score = sum(5 for token in tokens if token in label.split())
        score += sum(2 for token in tokens if token in description.split())
        score += sum(1 for token in tokens if token in conditions.split())
        if not score:
            continue
        institution = aide.get("institution") or {}
        matches.append((score, {
            "titre": aide.get("label", ""),
            "organisme": institution.get("label", "") if isinstance(institution, dict) else "",
            "description": _plain_text(aide.get("description"))[:500],
            "conditions": [_plain_text(c) for c in (aide.get("conditions") or [])[:5]],
            "criteres": aide.get("conditions_generales") or [],
            "montant": aide.get("montant"),
            "unite": aide.get("unit"),
            "periodicite": aide.get("periodicite"),
            "lien": aide.get("link"),
        }))
    matches.sort(key=lambda item: item[0], reverse=True)
    return [item for _, item in matches[:max(0, min(limit, MAX_RESULTS))]]

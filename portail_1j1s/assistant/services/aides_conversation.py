"""Extraction conversationnelle prudente des critères de recherche d'aides."""

import json
import re

from .albert import AlbertClient, AlbertAPIError

SITUATIONS = {
    "apprenti", "enseignement_superieur", "etudiant", "lyceen", "chomeur",
    "stagiaire", "service_civique", "salarie", "inactif", "independant",
    "beneficiaire_rsa", "professionnalisation", "parent", "collegien",
}


def interpret_aides(messages):
    """Extrait l'intention et les critères explicitement fournis dans le dialogue.

    Ne stocke pas de profil : l'historique de conversation existant fait foi.
    """
    instructions = (
        "Analyse cette conversation pour une recherche d'aides publiques françaises. "
        "Réponds UNIQUEMENT par un objet JSON avec les clés : "
        "recherche_aides (booléen), sujet (chaîne de mots-clés), "
        "age (entier ou null), departement (code INSEE département ou null), "
        "region (code INSEE région ou null), commune (code INSEE commune ou null), "
        "situation (chaîne ou null), besoin_precision (booléen). "
        "Utilise uniquement les renseignements explicitement donnés par l'utilisateur "
        "dans l'ensemble des échanges, jamais de supposition. "
        "Codes de situation autorisés : "
        + ", ".join(sorted(SITUATIONS))
        + ". recherche_aides est vrai pour les demandes d'aides, bourses, "
        "financements, réductions, droits, ou pour une réponse à une question "
        "précédente concernant ces aides. "
        "sujet doit décrire le besoin initial (permis, logement, etc.) "
        "et non simplement le dernier message. "
        "besoin_precision est vrai si l'âge ou le département manque et "
        "que la question est une recherche personnalisée. "
        "N'invente aucun code géographique ; utilise null en cas d'incertitude."
    )
    try:
        answer = AlbertClient().chat(
            [{"role": "system", "content": instructions}] + messages[-12:]
        )
        match = re.search(r"\{[\s\S]*\}", answer)
        data = json.loads(match.group(0)) if match else {}
    except (AlbertAPIError, ValueError, TypeError, AttributeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("recherche_aides"), bool):
        return None
    age = data.get("age")
    if not isinstance(age, int) or isinstance(age, bool) or not 0 <= age <= 120:
        age = None
    def code(key, max_length):
        value = data.get(key)
        if isinstance(value, (str, int)) and re.fullmatch(r"[0-9A-Za-z]{2," + str(max_length) + r"}", str(value)):
            return str(value).upper()
        return None

    situation = data.get("situation")
    if situation not in SITUATIONS:
        situation = None
    sujet = data.get("sujet")
    if not isinstance(sujet, str) or not sujet.strip():
        sujet = ""
    return {
        "recherche_aides": data["recherche_aides"],
        "sujet": sujet[:180],
        "age": age,
        "departement": code("departement", 3),
        "region": code("region", 2),
        "commune": code("commune", 5),
        "situation": situation,
        "besoin_precision": data.get("besoin_precision") is True,
    }

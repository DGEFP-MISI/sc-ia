import os

import requests


class AlbertAPIError(Exception):
    """Erreur lors d'un appel à Albert API."""


class AlbertClient:
    """Client pour communiquer avec Albert API."""

    def __init__(self):
        self.base_url = os.environ.get("ALBERT_API_URL", "").rstrip("/")
        self.api_key = os.environ.get("ALBERT_API_KEY", "")
        self.model = os.environ.get("ALBERT_MODEL", "")

    def chat(self, messages):
        if not all([self.base_url, self.api_key, self.model]):
            raise AlbertAPIError(
                "La configuration Albert API est incomplète."
            )

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )

            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        except (
            requests.RequestException,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            raise AlbertAPIError(
                "Impossible d'obtenir une réponse d'Albert API."
            ) from exc

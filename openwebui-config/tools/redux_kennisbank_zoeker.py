"""
title: Redux Kennisbank Zoeker
description: Zoekt live in de Redux Gaming kennisbank via directe Qdrant + Ollama integratie. Geen HTTP timeout issues. Altijd actueel.
author: Redux Gaming
version: 4.0
"""

import json
import urllib.request
from typing import Optional


OLLAMA_URL = "http://ollama:11434"
QDRANT_URL = "http://qdrant:6333"
EMBED_MODEL = "bge-m3:latest"
COLLECTION = "open-webui_knowledge"


def _embed(text: str) -> list:
    """Genereer embedding via Ollama."""
    body = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    return data["embedding"]


def _search_qdrant(embedding: list, k: int = 5, score_threshold: float = 0.3) -> list:
    """Zoek in Qdrant met cosine similarity."""
    body = json.dumps({
        "vector": embedding,
        "limit": k,
        "score_threshold": score_threshold,
        "with_payload": True,
        "with_vector": False
    }).encode()
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("result", [])


class Tools:
    def __init__(self):
        pass

    def zoek_product(
        self,
        query: str,
        max_results: int = 5,
        __user__: dict = {},
    ) -> str:
        """
        Zoekt in de Redux Gaming productcatalogus naar actuele prijzen, specs en beschikbaarheid.
        Gebruik voor: gaming PCs, controllers, muizen, keyboards, headsets, monitoren,
        muismatten, accessoires — alles wat Redux Gaming verkoopt.

        :param query: Bijv. "ASUS ROG Raikiri Pro prijs", "RTX 5080 gaming PC specs"
        :param max_results: Aantal resultaten (standaard 5)
        :return: Gevonden productinfo met prijzen uit de kennisbank
        """
        if not query.strip():
            return "Geef een zoekterm op."

        try:
            embedding = _embed(query)
            results = _search_qdrant(embedding, k=max_results)

            if not results:
                return f"Geen resultaten gevonden voor: '{query}'."

            output_parts = [f"Resultaten voor '{query}':\n"]
            for i, hit in enumerate(results, 1):
                text = hit.get("payload", {}).get("text", "")
                score = hit.get("score", 0)
                if text:
                    output_parts.append(f"--- Resultaat {i} (score: {score:.2f}) ---\n{text}")

            return "\n\n".join(output_parts).strip()

        except Exception as e:
            return f"Fout bij zoeken: {e}"

    def zoek_hr(
        self,
        query: str,
        max_results: int = 3,
        __user__: dict = {},
    ) -> str:
        """
        Zoekt in de HR/CAO kennisbank naar verlofregels, arbeidsvoorwaarden en procedures.

        :param query: Bijv. "vakantiedagen fulltime", "ziekmelding procedure"
        :param max_results: Aantal resultaten
        :return: HR-informatie uit de kennisbank
        """
        return self.zoek_product(query=query, max_results=max_results, __user__=__user__)

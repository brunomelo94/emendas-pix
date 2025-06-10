"""Fetch Brazilian politicians' party info from Wikipedia."""
from __future__ import annotations

import json
import logging
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

WIKI_API = "https://pt.wikipedia.org/w/api.php"

# Mapping of common party names to their acronyms
PARTY_MAP = {
    "PARTIDO DOS TRABALHADORES": "PT",
    "PARTIDO LIBERAL": "PL",
    "PARTIDO PROGRESSISTA": "PP",
    "MOVIMENTO DEMOCRÁTICO BRASILEIRO": "MDB",
    "UNIÃO BRASIL": "UNIÃO",
    "PARTIDO SOCIAL CRISTÃO": "PSC",
    "PARTIDO SOCIAL DEMOCRÁTICO": "PSD",
    "PARTIDO VERDE": "PV",
    "PARTIDO DA SOCIAL DEMOCRACIA BRASILEIRA": "PSDB",
    "PARTIDO SOCIALISMO E LIBERDADE": "PSOL",
    "PARTIDO DEMOCRÁTICO TRABALHISTA": "PDT",
    "PARTIDO REPUBLICANO PROGRESSISTA": "PRP",
    "CIDADANIA": "CIDADANIA",
    "PARTIDO SOCIALISTA BRASILEIRO": "PSB",
    "PARTIDO COMUNISTA DO BRASIL": "PCdoB",
    "PODEMOS": "PODE",
    "REPUBLICANOS": "REPUBLICANOS",
    "SOLIDARIEDADE": "SOLIDARIEDADE",
    "REDE SUSTENTABILIDADE": "REDE",
}


def _get_wikitext(title: str) -> str | None:
    """Return page wikitext for *title* if available."""
    url = f"{WIKI_API}?action=parse&page={quote(title)}&prop=wikitext&format=json&formatversion=2"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req) as resp:
            data = json.load(resp)
    except Exception as exc:  # pragma: no cover - network issues
        logger.warning("Wiki request failed for %s: %s", title, exc)
        return None
    return data.get("parse", {}).get("wikitext")


def _search_title(name: str) -> str | None:
    """Return first page title from a Wikipedia search."""
    url = f"{WIKI_API}?action=query&list=search&srsearch={quote(name)}&utf8=&format=json"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req) as resp:
            data = json.load(resp)
    except Exception as exc:  # pragma: no cover - network issues
        logger.warning("Wiki search failed for %s: %s", name, exc)
        return None
    results = data.get("query", {}).get("search")
    if results:
        return results[0].get("title")
    return None


PARTY_RE = re.compile(r"\|\s*(?:Partido[\w\s]*|Filia[cç][aã]o)[^=]*=\s*([^\n|]+)", re.IGNORECASE)


def fetch_party_from_wikipedia(name: str) -> str | None:
    """Fetch party acronym for *name* from Wikipedia."""
    title = name.replace(" ", "_")
    wikitext = _get_wikitext(title)
    if not wikitext:
        search_title = _search_title(name)
        if search_title:
            wikitext = _get_wikitext(search_title)
    if not wikitext:
        return None

    match = PARTY_RE.search(wikitext)
    if not match:
        return None

    party_text = match.group(1)
    # Drop HTML tags and wiki links
    party_text = re.sub(r"<.*?>", "", party_text)
    party_text = party_text.replace("[[", "").replace("]]", "")
    party_text = re.sub(r"\{\{.*?\}\}", "", party_text)
    # Only keep last party listed
    if "<br>" in party_text:
        party_text = party_text.split("<br>")[-1]
    if "|" in party_text:
        party_text = party_text.split("|")[-1]
    party_text = party_text.strip()
    party_text = re.sub(r"\(.*?\)", "", party_text).strip()
    party_text_upper = party_text.upper()
    # Map full party name to acronym if available
    if party_text_upper in PARTY_MAP:
        return PARTY_MAP[party_text_upper]
    if party_text_upper:
        return party_text_upper
    return None

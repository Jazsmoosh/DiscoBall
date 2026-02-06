import os
import requests
from rapidfuzz import fuzz

OMDB_URL = "https://www.omdbapi.com/"

def omdb_search_best(query):
    key = os.getenv("OMDB_API_KEY")
    if not key:
        return None
    r = requests.get(OMDB_URL, params={"apikey": key, "s": query}, timeout=15)
    r.raise_for_status()
    items = (r.json().get("Search") or [])[:10]
    if not items:
        return None
    best = None
    best_score = 0.0
    for it in items:
        score = fuzz.token_set_ratio(query.lower(), (it.get("Title") or "").lower()) / 100.0
        if score > best_score:
            best_score = score
            best = it
    if not best:
        return None
    imdb = best.get("imdbID")
    d = requests.get(OMDB_URL, params={"apikey": key, "i": imdb, "plot": "short"}, timeout=15)
    d.raise_for_status()
    det = d.json()
    year = det.get("Year")
    year = int(year[:4]) if isinstance(year, str) and year[:4].isdigit() else None
    genres = [g.strip() for g in (det.get("Genre") or "").split(",") if g.strip()]
    primary = genres[0] if genres else None
    return {"type": "movie", "title": det.get("Title") or query, "year": year, "genres": genres, "primary_genre": primary, "imdb_id": imdb, "confidence": max(0.0, min(1.0, best_score))}

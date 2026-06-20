from __future__ import annotations

import re
from typing import Any

import requests
from rapidfuzz import fuzz

from ..models import MediaMatch, TitleGuess
from ..utils import log

OMDB_URL = "https://www.omdbapi.com/"


class OMDbProvider:
    name = "omdb"

    def __init__(self, api_key: str | None, timeout: int = 15) -> None:
        self.api_key = api_key
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, guess: TitleGuess, media_type: str = "movie", limit: int = 10) -> list[MediaMatch]:
        if not self.enabled or not guess.query.strip():
            return []
        try:
            candidates = self._search_candidates(guess, media_type, limit)
            return [self._details(item, guess, media_type) for item in candidates]
        except requests.RequestException as exc:
            log.warning("OMDb request failed: %s", exc)
            return []
        except Exception as exc:  # bad provider payloads should not kill the watcher
            log.warning("OMDb provider failed: %s", exc)
            return []

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        params = {**params, "apikey": self.api_key}
        response = requests.get(OMDB_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "False":
            return {}
        return data

    def _search_candidates(self, guess: TitleGuess, media_type: str, limit: int) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"s": guess.query}
        if guess.year:
            params["y"] = str(guess.year)
        if media_type in {"movie", "series", "episode"}:
            params["type"] = "series" if media_type == "series" else "movie"
        data = self._request(params)
        items = data.get("Search") or []

        # Retry without year because OMDb years can be ranges, alternates, or original releases.
        if not items and guess.year:
            params.pop("y", None)
            data = self._request(params)
            items = data.get("Search") or []

        scored = []
        for item in items[: max(limit, 10)]:
            title = item.get("Title") or ""
            score = fuzz.token_set_ratio(guess.query.lower(), title.lower()) / 100.0
            item_year = _first_year(item.get("Year"))
            if guess.year and item_year == guess.year:
                score += 0.12
            if item.get("Type") == "movie":
                score += 0.03
            scored.append((min(score, 1.0), item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def _details(self, item: dict[str, Any], guess: TitleGuess, requested_type: str) -> MediaMatch:
        imdb_id = item.get("imdbID")
        detail = self._request({"i": imdb_id, "plot": "short"}) if imdb_id else item
        if not detail:
            detail = item
        title = detail.get("Title") or item.get("Title") or guess.query
        year = _first_year(detail.get("Year") or item.get("Year"))
        genres = [g.strip() for g in (detail.get("Genre") or "").split(",") if g.strip() and g.strip() != "N/A"]
        score = fuzz.token_set_ratio(guess.query.lower(), title.lower()) / 100.0
        if guess.year and year == guess.year:
            score += 0.14
        if detail.get("Type") == "movie" or requested_type == "movie":
            score += 0.02
        return MediaMatch(
            media_type=detail.get("Type") or requested_type or "movie",
            title=title,
            year=year,
            genres=genres,
            primary_genre=genres[0] if genres else None,
            imdb_id=imdb_id,
            provider=self.name,
            confidence=max(0.0, min(1.0, score)),
            raw={k: detail.get(k) for k in ("Title", "Year", "Rated", "Released", "Runtime", "Genre", "Director", "imdbRating")},
        )


def _first_year(value: Any) -> int | None:
    if not value:
        return None
    m = re.search(r"(?:19|20)\d{2}", str(value))
    return int(m.group(0)) if m else None

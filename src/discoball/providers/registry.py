from __future__ import annotations

from ..config import Config
from ..models import MediaMatch, TitleGuess
from ..utils import log
from .imdb_dataset import IMDbDatasetProvider
from .omdb import OMDbProvider


def find_best_match(guess: TitleGuess, cfg: Config, media_type: str = "movie") -> MediaMatch | None:
    providers = []
    names = cfg.providers or ["omdb", "imdb"]
    if "omdb" in names:
        providers.append(OMDbProvider(cfg.omdb_api_key))
    if "imdb" in names:
        providers.append(IMDbDatasetProvider(cfg.imdb_sqlite_path))

    all_matches: list[MediaMatch] = []
    for provider in providers:
        if not provider.enabled:
            log.debug("provider disabled: %s", provider.name)
            continue
        matches = provider.search(guess, media_type=media_type)
        log.info("provider=%s query=%r matches=%s", provider.name, guess.query, len(matches))
        all_matches.extend(matches)

    if not all_matches:
        return None
    all_matches.sort(key=lambda m: (m.confidence, 1 if m.provider == "omdb" else 0), reverse=True)
    return all_matches[0]

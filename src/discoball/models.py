from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TitleGuess:
    query: str
    year: int | None = None
    source_path: str = ""
    used_path_part: str = ""


@dataclass(slots=True)
class MediaMatch:
    media_type: str = "movie"
    title: str = ""
    year: int | None = None
    genres: list[str] = field(default_factory=list)
    primary_genre: str | None = None
    imdb_id: str | None = None
    provider: str = "unknown"
    confidence: float = 0.0
    source: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

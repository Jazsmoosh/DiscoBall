from __future__ import annotations

import os
from pathlib import Path

from .config import Config
from .models import MediaMatch
from .utils import safe_name


def _base_name(match: MediaMatch, cfg: Config, *, include_tags: bool = True) -> str:
    title = safe_name(match.title or "Unknown")
    base = title
    if match.year:
        base += f" ({match.year})"
    if include_tags and cfg.include_genre_tag and match.primary_genre:
        base += f" [{safe_name(match.primary_genre)}]"
    if include_tags and cfg.include_source_tag and match.source:
        base += f" {{{safe_name(match.source)}}}"
    return safe_name(base)


def build_destination(match: MediaMatch, src_path: str, output_root: str, cfg: Config) -> tuple[str, str]:
    ext = Path(src_path).suffix.lower()
    if match.media_type in {"episode", "series"}:
        root = Path(output_root) / cfg.tv_root_subdir if cfg.tv_root_subdir else Path(output_root)
    else:
        root = Path(output_root) / cfg.movie_root_subdir if cfg.movie_root_subdir else Path(output_root)

    if cfg.naming_style == "plex":
        # Plex-style naming keeps metadata tags out of the actual file/folder name.
        base = _base_name(match, cfg, include_tags=False)
    else:
        base = _base_name(match, cfg, include_tags=True)

    folder = root / base
    return str(folder), base + ext


def build_unmatched_destination(src_path: str, output_root: str, cfg: Config) -> tuple[str, str]:
    p = Path(src_path)
    folder = Path(output_root) / cfg.unmatched_subdir
    return str(folder), safe_name(p.stem) + p.suffix.lower()

from __future__ import annotations

import os
import re
from pathlib import Path

from .models import TitleGuess

GENERIC_RIP_RE = re.compile(
    r"^(?:title[_ .-]*t?\d{1,3}|title\d{1,3}|feature|main[_ .-]*feature|movie|segment\d+|vts[_ .-]*\d+[_ .-]*\d+)$",
    re.IGNORECASE,
)
DISC_PART_RE = re.compile(r"^(?:disc|disk|dvd|bd|blu[-_ .]?ray|uhd|video_ts|bdmv)[-_ .]*\d*$", re.IGNORECASE)
YEAR_RE = re.compile(r"(?:^|[^0-9])((?:19|20)\d{2})(?:[^0-9]|$)")

JUNK_TOKENS = {
    "mkv", "mp4", "avi", "mov", "wmv", "dvd", "dvdrip", "bdrip", "bluray", "blu", "ray",
    "uhd", "2160p", "1080p", "720p", "480p", "x264", "x265", "h264", "h265", "hevc", "aac",
    "dts", "truehd", "atmos", "remux", "proper", "repack", "makemkv", "handbrake", "encoded", "rip",
    "title", "feature", "main", "movie", "disc", "disk",
}


def is_generic_rip_name(stem: str) -> bool:
    s = stem.strip().lower()
    return bool(GENERIC_RIP_RE.match(s))


def _clean_piece(value: str) -> tuple[str, int | None]:
    s = value.replace("_", " ").replace(".", " ").replace("-", " ")
    year = None
    m = YEAR_RE.search(s)
    if m:
        year = int(m.group(1))
    s = re.sub(r"[\[\]{}()]+", " ", s)
    tokens = []
    for token in re.findall(r"[A-Za-z0-9']+", s):
        if token.lower() in JUNK_TOKENS:
            continue
        if re.fullmatch(r"t?\d{1,3}", token.lower()):
            continue
        tokens.append(token)
    clean = " ".join(tokens).strip()
    return clean, year


def guess_from_path(path: str, prefer_parent_for_generic: bool = True) -> TitleGuess:
    p = Path(path)
    stem = p.stem
    used = stem

    # MakeMKV often emits title_t00.mkv. If the file name is generic, use the nearest
    # meaningful parent folder, such as /watch/Half Baked (1998)/title_t00.mkv.
    if prefer_parent_for_generic and is_generic_rip_name(stem):
        for part in reversed(p.parent.parts):
            if part in {os.sep, "", "."}:
                continue
            if DISC_PART_RE.match(part):
                continue
            if is_generic_rip_name(part):
                continue
            used = part
            break

    query, year = _clean_piece(used)
    if not query and used != stem:
        query, year = _clean_piece(stem)
    return TitleGuess(query=query or stem, year=year, source_path=str(p), used_path_part=used)

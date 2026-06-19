from __future__ import annotations

import csv
import gzip
import os
from pathlib import Path
import re
import sqlite3
from typing import Iterable

from rapidfuzz import fuzz

from ..models import MediaMatch, TitleGuess
from ..utils import log

MOVIE_TYPES = {"movie", "tvMovie", "video", "tvSpecial"}


class IMDbDatasetProvider:
    """Offline IMDb provider backed by IMDb's non-commercial TSV datasets.

    Build once with:
      discoball imdb-index --dataset-dir /imdb --db /config/imdb.sqlite
    """

    name = "imdb"

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    @property
    def enabled(self) -> bool:
        return Path(self.sqlite_path).is_file()

    def search(self, guess: TitleGuess, media_type: str = "movie", limit: int = 10) -> list[MediaMatch]:
        if not self.enabled or not guess.query.strip():
            return []
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = _query(conn, guess.query, limit=50)
        except sqlite3.Error as exc:
            log.warning("IMDb dataset query failed: %s", exc)
            return []

        matches: list[MediaMatch] = []
        for row in rows:
            title = row["primaryTitle"] or row["originalTitle"] or guess.query
            year = int(row["startYear"]) if str(row["startYear"]).isdigit() else None
            genres = [] if not row["genres"] or row["genres"] == "\\N" else [g.strip() for g in row["genres"].split(",") if g.strip()]
            score = fuzz.token_set_ratio(guess.query.lower(), title.lower()) / 100.0
            if guess.year and year == guess.year:
                score += 0.14
            if row["titleType"] in MOVIE_TYPES:
                score += 0.03
            matches.append(MediaMatch(
                media_type="movie" if row["titleType"] in MOVIE_TYPES else str(row["titleType"]),
                title=title,
                year=year,
                genres=genres,
                primary_genre=genres[0] if genres else None,
                imdb_id=row["tconst"],
                provider=self.name,
                confidence=max(0.0, min(1.0, score)),
                raw={"titleType": row["titleType"], "originalTitle": row["originalTitle"]},
            ))
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:limit]


def build_index(dataset_dir: str, db_path: str) -> None:
    basics = Path(dataset_dir) / "title.basics.tsv.gz"
    if not basics.is_file():
        raise FileNotFoundError(f"Missing {basics}")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    tmp_path = db_path + ".tmp"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    with sqlite3.connect(tmp_path) as conn:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.executescript(
            """
            CREATE TABLE titles (
                tconst TEXT PRIMARY KEY,
                titleType TEXT,
                primaryTitle TEXT,
                originalTitle TEXT,
                isAdult INTEGER,
                startYear TEXT,
                endYear TEXT,
                runtimeMinutes TEXT,
                genres TEXT
            );
            CREATE VIRTUAL TABLE title_fts USING fts5(
                tconst UNINDEXED,
                primaryTitle,
                originalTitle,
                titleType UNINDEXED,
                startYear UNINDEXED,
                genres UNINDEXED
            );
            """
        )
        rows = 0
        with gzip.open(basics, "rt", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            batch = []
            fts_batch = []
            for r in reader:
                if r.get("isAdult") == "1":
                    continue
                if r.get("titleType") not in MOVIE_TYPES:
                    continue
                item = (
                    r.get("tconst"), r.get("titleType"), r.get("primaryTitle"), r.get("originalTitle"),
                    int(r.get("isAdult") or 0), r.get("startYear"), r.get("endYear"), r.get("runtimeMinutes"), r.get("genres"),
                )
                batch.append(item)
                fts_batch.append((r.get("tconst"), r.get("primaryTitle"), r.get("originalTitle"), r.get("titleType"), r.get("startYear"), r.get("genres")))
                if len(batch) >= 5000:
                    conn.executemany("INSERT INTO titles VALUES (?,?,?,?,?,?,?,?,?)", batch)
                    conn.executemany("INSERT INTO title_fts VALUES (?,?,?,?,?,?)", fts_batch)
                    rows += len(batch)
                    batch.clear(); fts_batch.clear()
                    if rows % 100000 == 0:
                        log.info("indexed %s IMDb titles", rows)
            if batch:
                conn.executemany("INSERT INTO titles VALUES (?,?,?,?,?,?,?,?,?)", batch)
                conn.executemany("INSERT INTO title_fts VALUES (?,?,?,?,?,?)", fts_batch)
                rows += len(batch)
        conn.commit()
        conn.execute("VACUUM")
    os.replace(tmp_path, db_path)
    log.info("IMDb index ready: %s titles at %s", rows, db_path)


def _query(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    terms = _fts_terms(query)
    if not terms:
        return []
    sql = """
        SELECT t.tconst, t.titleType, t.primaryTitle, t.originalTitle, t.startYear, t.genres
        FROM title_fts f
        JOIN titles t ON t.tconst = f.tconst
        WHERE title_fts MATCH ?
        LIMIT ?
    """
    return list(conn.execute(sql, (terms, limit)))


def _fts_terms(query: str) -> str:
    tokens = [t for t in re.findall(r"[A-Za-z0-9]+", query) if len(t) > 1 and not re.fullmatch(r"(?:19|20)\d{2}", t)]
    # AND terms narrows common titles; prefix matching helps apostrophes/plurals.
    return " ".join(f"{t}*" for t in tokens[:6])

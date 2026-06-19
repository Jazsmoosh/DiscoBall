from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from .utils import env_bool, env_float, env_int, split_csv


@dataclass(slots=True)
class Config:
    watch_dir: str = "/watch"
    output_dir: str = "/output"
    config_dir: str = "/config"
    stable_time: int = 120
    check_interval: int = 30
    extensions: list[str] | None = None
    dry_run: bool = False
    min_confidence: float = 0.64
    min_video_size_mb: int = 50
    source_tag_default: str = "DVD"
    include_genre_tag: bool = True
    include_source_tag: bool = True
    movie_root_subdir: str = ""
    tv_root_subdir: str = "TV"
    unmatched_subdir: str = "_Unmatched"
    file_action: str = "move"  # move, copy, hardlink
    conflict_policy: str = "suffix"  # suffix, skip, overwrite
    ui_enabled: bool = False
    ui_port: int = 8000
    providers: list[str] | None = None
    omdb_api_key: str | None = None
    imdb_sqlite_path: str = "/config/imdb.sqlite"
    prefer_parent_for_generic: bool = True
    naming_style: str = "discoball"  # discoball or plex

    @classmethod
    def from_env(cls) -> "Config":
        cfg = cls(
            watch_dir=os.getenv("WATCH_DIR", "/watch"),
            output_dir=os.getenv("OUTPUT_DIR", "/output"),
            config_dir=os.getenv("CONFIG_DIR", "/config"),
            stable_time=env_int("STABLE_TIME_SECONDS", 120),
            check_interval=env_int("CHECK_INTERVAL_SECONDS", 30),
            extensions=[e.lower().lstrip(".") for e in split_csv(os.getenv("VIDEO_EXTENSIONS"), ["mkv", "mp4"])],
            dry_run=env_bool("DRY_RUN", False),
            min_confidence=env_float("MIN_CONFIDENCE", 0.64),
            min_video_size_mb=env_int("MIN_VIDEO_SIZE_MB", 50),
            source_tag_default=os.getenv("SOURCE_TAG_DEFAULT", "DVD"),
            include_genre_tag=env_bool("INCLUDE_GENRE_TAG", True),
            include_source_tag=env_bool("INCLUDE_SOURCE_TAG", True),
            movie_root_subdir=os.getenv("MOVIE_ROOT_SUBDIR", ""),
            tv_root_subdir=os.getenv("TV_ROOT_SUBDIR", "TV"),
            unmatched_subdir=os.getenv("UNMATCHED_SUBDIR", "_Unmatched"),
            file_action=os.getenv("FILE_ACTION", "move").lower(),
            conflict_policy=os.getenv("CONFLICT_POLICY", "suffix").lower(),
            ui_enabled=env_bool("UI_ENABLED", False),
            ui_port=env_int("UI_PORT", 8000),
            providers=[p.lower() for p in split_csv(os.getenv("PROVIDERS"), ["omdb", "imdb"] )],
            omdb_api_key=os.getenv("OMDB_API_KEY"),
            imdb_sqlite_path=os.getenv("IMDB_SQLITE_PATH", "/config/imdb.sqlite"),
            prefer_parent_for_generic=env_bool("PREFER_PARENT_FOR_GENERIC", True),
            naming_style=os.getenv("NAMING_STYLE", "discoball").lower(),
        )
        if cfg.file_action not in {"move", "copy", "hardlink"}:
            cfg.file_action = "move"
        if cfg.conflict_policy not in {"suffix", "skip", "overwrite"}:
            cfg.conflict_policy = "suffix"
        if cfg.naming_style not in {"discoball", "plex"}:
            cfg.naming_style = "discoball"
        Path(cfg.config_dir).mkdir(parents=True, exist_ok=True)
        return cfg

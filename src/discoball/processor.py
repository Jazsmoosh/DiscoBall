from __future__ import annotations

import json
import os
from pathlib import Path
from dataclasses import asdict
import shutil
import time

from .config import Config
from .guess import guess_from_path
from .models import MediaMatch
from .naming import build_destination, build_unmatched_destination
from .providers.registry import find_best_match
from .state import incr, update
from .utils import log


def is_video(path: str, extensions: list[str]) -> bool:
    return Path(path).is_file() and Path(path).suffix.lower().lstrip(".") in set(extensions)


def process_file(src_path: str, cfg: Config) -> str | None:
    p = Path(src_path)
    if not p.exists():
        update(phase="idle", detail=f"Skipped missing file: {src_path}")
        return None
    min_bytes = cfg.min_video_size_mb * 1024 * 1024
    if p.stat().st_size < min_bytes:
        update(phase="skipped", current_file=str(p), detail=f"Below MIN_VIDEO_SIZE_MB={cfg.min_video_size_mb}")
        log.info("skip below min size: %s", p)
        return None

    update(phase="identifying", current_file=str(p), detail="Guessing title from path")
    guess = guess_from_path(str(p), cfg.prefer_parent_for_generic)
    update(detail=f"Query: {guess.query}")
    match = find_best_match(guess, cfg, media_type="movie")

    unmatched_reason = None
    if not match:
        unmatched_reason = "No metadata provider returned a match"
    elif match.confidence < cfg.min_confidence:
        unmatched_reason = f"Low confidence {match.confidence:.2f} < {cfg.min_confidence:.2f}"

    if unmatched_reason:
        log.warning("unmatched %s: %s", p, unmatched_reason)
        match = MediaMatch(
            media_type="unknown",
            title=guess.query or p.stem,
            year=guess.year,
            provider="none",
            confidence=0.0,
            source=cfg.source_tag_default,
            raw={"reason": unmatched_reason, "guess": asdict(guess)},
        )
        dest_dir, dest_file = build_unmatched_destination(str(p), cfg.output_dir, cfg)
    else:
        match.source = cfg.source_tag_default
        dest_dir, dest_file = build_destination(match, str(p), cfg.output_dir, cfg)

    dest_path = _resolve_conflict(Path(dest_dir) / dest_file, cfg.conflict_policy)
    if dest_path is None:
        update(phase="skipped", detail="Destination exists and CONFLICT_POLICY=skip")
        return None

    sidecar_path = dest_path.with_suffix(dest_path.suffix + ".discoball.json")
    payload = {
        "source": str(p),
        "destination": str(dest_path),
        "match": match.to_dict(),
        "unmatched_reason": unmatched_reason,
        "processed_at": time.time(),
        "file_action": cfg.file_action,
    }

    log.info("destination: %s", dest_path)
    update(phase="dry-run" if cfg.dry_run else "moving", detail=str(dest_path))
    if cfg.dry_run:
        return str(dest_path)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    _transfer_file(p, dest_path, cfg.file_action)
    with sidecar_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    incr("processed")
    update(phase="done", current_file="", last_done=str(dest_path), last_done_at=time.time(), detail="")
    return str(dest_path)


def _resolve_conflict(path: Path, policy: str) -> Path | None:
    if not path.exists():
        return path
    if policy == "overwrite":
        return path
    if policy == "skip":
        return None
    stem, suffix = path.stem, path.suffix
    for i in range(2, 1000):
        candidate = path.with_name(f"{stem} - {i}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not resolve destination conflict for {path}")


def _transfer_file(src: Path, dest: Path, action: str) -> None:
    if action == "copy":
        shutil.copy2(src, dest)
    elif action == "hardlink":
        try:
            os.link(src, dest)
            src.unlink()
        except OSError:
            shutil.move(str(src), str(dest))
    else:
        shutil.move(str(src), str(dest))

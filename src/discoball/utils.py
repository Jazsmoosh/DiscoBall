from __future__ import annotations

import logging
import os
import re
import unicodedata
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("discoball")


def truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def env_bool(name: str, default: bool = False) -> bool:
    return truthy(os.getenv(name), default)


def env_int(name: str, default: int) -> int:
    try:
        return int(str(os.getenv(name, str(default))).strip())
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    try:
        return float(str(os.getenv(name, str(default))).strip())
    except ValueError:
        return default


def split_csv(value: str | None, default: list[str] | None = None) -> list[str]:
    if value is None:
        return list(default or [])
    return [x.strip() for x in value.split(",") if x.strip()]


def safe_name(value: str, max_len: int = 180) -> str:
    """Return a filename safe on Windows, macOS, Linux, SMB, and ZFS shares."""
    s = unicodedata.normalize("NFKC", value or "")
    # Windows invalid chars plus control characters.
    s = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    if not s:
        s = "Unknown"
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if s.upper() in reserved:
        s = f"_{s}"
    return s[:max_len].rstrip(" .") or "Unknown"


def path_is_inside(child: str | Path, parent: str | Path) -> bool:
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False

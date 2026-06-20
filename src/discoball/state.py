from __future__ import annotations

from dataclasses import asdict, dataclass
import threading
import time


@dataclass
class Status:
    phase: str = "idle"
    current_file: str = ""
    detail: str = ""
    processed: int = 0
    errors: int = 0
    queued: int = 0
    last_done: str = ""
    last_done_at: float = 0.0
    last_error: str = ""
    stable_target: int = 0
    stable_elapsed: int = 0
    updated_at: float = 0.0


_lock = threading.Lock()
_status = Status()


def update(**kwargs) -> None:
    with _lock:
        for key, value in kwargs.items():
            if hasattr(_status, key):
                setattr(_status, key, value)
        _status.updated_at = time.time()


def incr(field: str, amount: int = 1) -> None:
    with _lock:
        if hasattr(_status, field):
            setattr(_status, field, getattr(_status, field) + amount)
        _status.updated_at = time.time()


def snapshot() -> dict:
    with _lock:
        return asdict(_status)

from __future__ import annotations

from pathlib import Path
import queue
import threading
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from .config import Config
from .processor import is_video, process_file
from .state import incr, update
from .utils import log, path_is_inside


class StableWatcher:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.q: queue.Queue[str] = queue.Queue()
        self.queued: set[str] = set()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def enqueue(self, path: str) -> None:
        p = str(Path(path))
        if not is_video(p, self.cfg.extensions or []):
            return
        # Avoid loops when output lives inside watch.
        if path_is_inside(p, self.cfg.output_dir):
            return
        with self.lock:
            if p in self.queued:
                return
            self.queued.add(p)
            update(queued=len(self.queued))
        log.info("queued: %s", p)
        self.q.put(p)

    def scan_existing(self) -> None:
        root = Path(self.cfg.watch_dir)
        for path in root.rglob("*"):
            if self.stop_event.is_set():
                return
            self.enqueue(str(path))

    def worker(self) -> None:
        while not self.stop_event.is_set():
            try:
                path = self.q.get(timeout=1)
            except queue.Empty:
                continue
            try:
                if wait_stable(path, self.cfg.stable_time, self.cfg.check_interval):
                    process_file(path, self.cfg)
            except Exception as exc:
                log.exception("failed processing %s", path)
                incr("errors")
                update(phase="error", current_file="", last_error=f"{path}: {exc}")
            finally:
                with self.lock:
                    self.queued.discard(path)
                    update(queued=len(self.queued))
                self.q.task_done()


def wait_stable(path: str, stable_time: int, interval: int) -> bool:
    stable_elapsed = 0
    last_size = -1
    last_mtime = -1.0
    update(phase="stabilizing", current_file=path, stable_target=stable_time, stable_elapsed=0, detail="Waiting for MakeMKV/HandBrake to finish writing")
    while stable_elapsed < stable_time:
        p = Path(path)
        if not p.exists():
            update(phase="skipped", current_file="", detail=f"File disappeared before stable: {path}")
            return False
        stat = p.stat()
        if stat.st_size > 0 and stat.st_size == last_size and stat.st_mtime == last_mtime:
            stable_elapsed += interval
        else:
            stable_elapsed = 0
            last_size = stat.st_size
            last_mtime = stat.st_mtime
        update(stable_elapsed=min(stable_elapsed, stable_time))
        time.sleep(interval)
    return True


class Handler(FileSystemEventHandler):
    def __init__(self, watcher: StableWatcher) -> None:
        self.watcher = watcher

    def on_created(self, event):
        if not event.is_directory:
            self.watcher.enqueue(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.watcher.enqueue(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.watcher.enqueue(event.dest_path)


def run_watcher(cfg: Config, scan_first: bool = True) -> None:
    watch_dir = Path(cfg.watch_dir)
    if not watch_dir.is_dir():
        raise SystemExit(f"WATCH_DIR missing: {watch_dir}")
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)

    svc = StableWatcher(cfg)
    worker = threading.Thread(target=svc.worker, daemon=True, name="discoball-worker")
    worker.start()

    observer = PollingObserver(timeout=1)
    observer.schedule(Handler(svc), str(watch_dir), recursive=True)
    observer.start()
    update(phase="watching", detail=f"Watching {watch_dir}")
    log.info("watching: %s", watch_dir)

    if scan_first:
        svc.scan_existing()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        svc.stop_event.set()
        observer.stop()
        observer.join()

import os
import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from discoball.processor import process_file
from discoball.utils import log

def is_video(p, exts):
    return os.path.isfile(p) and os.path.splitext(p)[1].lower().lstrip(".") in exts

def wait_stable(p, stable_time, interval):
    last = -1
    stable = 0
    while stable < stable_time:
        try:
            size = os.path.getsize(p)
        except FileNotFoundError:
            return False
        if size == last and size > 0:
            stable += interval
        else:
            stable = 0
            last = size
        time.sleep(interval)
    return True

class Handler(FileSystemEventHandler):
    def __init__(self, outdir, stable_time, interval, exts, dry):
        self.outdir = outdir
        self.stable_time = stable_time
        self.interval = interval
        self.exts = exts
        self.dry = dry
    def on_created(self, e):
        if e.is_directory:
            return
        p = e.src_path
        if not is_video(p, self.exts):
            return
        log.info("new: %s", p)
        if wait_stable(p, self.stable_time, self.interval):
            process_file(p, self.outdir, dry_run=self.dry)

def run_watcher(watch_dir, output_dir, stable_time, interval, exts, dry_run):
    if not os.path.isdir(watch_dir):
        raise SystemExit("WATCH_DIR missing: " + watch_dir)
    os.makedirs(output_dir, exist_ok=True)
    obs = PollingObserver(timeout=1)
    obs.schedule(Handler(output_dir, stable_time, interval, exts, dry_run), watch_dir, recursive=True)
    obs.start()
    log.info("Watching: %s", watch_dir)
    try:
        while True:
            time.sleep(5)
    finally:
        obs.stop()
        obs.join()

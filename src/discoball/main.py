import argparse
import os
from discoball.watcher import run_watcher
from discoball.utils import log

def main():
    p = argparse.ArgumentParser(prog="discoball")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("watch")
    w.add_argument("--watch-dir", default=os.getenv("WATCH_DIR", "/watch"))
    w.add_argument("--output-dir", default=os.getenv("OUTPUT_DIR", "/output"))
    w.add_argument("--stable-time", type=int, default=int(os.getenv("STABLE_TIME_SECONDS", "120")))
    w.add_argument("--check-interval", type=int, default=int(os.getenv("CHECK_INTERVAL_SECONDS", "30")))
    w.add_argument("--extensions", default=os.getenv("VIDEO_EXTENSIONS", "mkv,mp4"))
    w.add_argument("--dry-run", action="store_true", default=False)
    a = p.parse_args()
    exts = [e.strip().lower().lstrip(".") for e in a.extensions.split(",") if e.strip()]
    log.info("watch=%s output=%s exts=%s", a.watch_dir, a.output_dir, exts)
    run_watcher(a.watch_dir, a.output_dir, a.stable_time, a.check_interval, exts, a.dry_run)

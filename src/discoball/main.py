from __future__ import annotations

import argparse
import sys
from pathlib import Path
from dataclasses import asdict

from .config import Config
from .guess import guess_from_path
from .providers.imdb_dataset import build_index
from .providers.registry import find_best_match
from .ui import start_ui
from .utils import log


def _base_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="discoball")
    sub = parser.add_subparsers(dest="cmd", required=True)

    watch = sub.add_parser("watch", help="watch a folder and process stable video files")
    watch.add_argument("--watch-dir")
    watch.add_argument("--output-dir")
    watch.add_argument("--stable-time", type=int)
    watch.add_argument("--check-interval", type=int)
    watch.add_argument("--extensions")
    watch.add_argument("--dry-run", action="store_true")
    watch.add_argument("--no-scan-first", action="store_true")

    scan = sub.add_parser("scan", help="process existing stable files once, then exit")
    scan.add_argument("--watch-dir")
    scan.add_argument("--output-dir")
    scan.add_argument("--dry-run", action="store_true")

    once = sub.add_parser("once", help="process a single file immediately")
    once.add_argument("path")
    once.add_argument("--output-dir")
    once.add_argument("--dry-run", action="store_true")

    ident = sub.add_parser("identify", help="show what DiscoBall would identify for a path or title")
    ident.add_argument("value")

    idx = sub.add_parser("imdb-index", help="build an optional local IMDb title index from title.basics.tsv.gz")
    idx.add_argument("--dataset-dir", required=True)
    idx.add_argument("--db", default=None)
    return parser


def _apply_common(cfg: Config, args: argparse.Namespace) -> Config:
    if getattr(args, "watch_dir", None):
        cfg.watch_dir = args.watch_dir
    if getattr(args, "output_dir", None):
        cfg.output_dir = args.output_dir
    if getattr(args, "stable_time", None) is not None:
        cfg.stable_time = args.stable_time
    if getattr(args, "check_interval", None) is not None:
        cfg.check_interval = args.check_interval
    if getattr(args, "extensions", None):
        cfg.extensions = [e.strip().lower().lstrip(".") for e in args.extensions.split(",") if e.strip()]
    if getattr(args, "dry_run", False):
        cfg.dry_run = True
    return cfg


def main(argv: list[str] | None = None) -> int:
    parser = _base_parser()
    args = parser.parse_args(argv)
    cfg = _apply_common(Config.from_env(), args)

    if args.cmd == "imdb-index":
        build_index(args.dataset_dir, args.db or cfg.imdb_sqlite_path)
        return 0

    if args.cmd == "identify":
        value = args.value
        guess = guess_from_path(value, cfg.prefer_parent_for_generic) if Path(value).suffix else guess_from_path(value + ".mkv", False)
        match = find_best_match(guess, cfg)
        print({"guess": asdict(guess), "match": match.to_dict() if match else None})
        return 0

    start_ui(cfg)

    if args.cmd == "once":
        from .processor import process_file
        cfg.output_dir = args.output_dir or cfg.output_dir
        result = process_file(args.path, cfg)
        print(result or "")
        return 0

    if args.cmd == "scan":
        from .watcher import StableWatcher
        cfg.stable_time = 0
        svc = StableWatcher(cfg)
        svc.scan_existing()
        while not svc.q.empty():
            path = svc.q.get()
            try:
                from .processor import process_file
                process_file(path, cfg)
            finally:
                svc.q.task_done()
        return 0

    if args.cmd == "watch":
        from .watcher import run_watcher
        run_watcher(cfg, scan_first=not args.no_scan_first)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())

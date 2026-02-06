import json
import os
import shutil
from discoball.providers.omdb import omdb_search_best
from discoball.naming import build_destination
from discoball.utils import log

def process_file(src_path, output_root, dry_run=False):
    guess = os.path.splitext(os.path.basename(src_path))[0].replace("_", " ").replace(".", " ").strip()
    match = omdb_search_best(guess) or {"type": "unknown", "title": guess, "year": None, "genres": [], "primary_genre": None, "confidence": 0.0}
    match["source"] = os.getenv("SOURCE_TAG_DEFAULT", "DVD")
    dest_dir, dest_file = build_destination(match, src_path, output_root)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, dest_file)
    sidecar = dest_path + ".discoball.json"
    payload = {"source": src_path, "match": match, "destination": dest_path}
    log.info("dest: %s", dest_path)
    if dry_run:
        log.info("dry-run: not moving")
        return
    shutil.move(src_path, dest_path)
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log.info("moved + sidecar: %s", sidecar)

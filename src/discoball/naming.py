import os

def truthy(env, default="0"):
    v = (os.getenv(env, default) or "").strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def safe_name(s):
    bad = "\\\\/:*?"
    bad = bad + chr(34) + chr(60) + chr(62) + chr(124)
    for ch in bad:
        s = s.replace(ch, "")
    s = " ".join(s.split()).strip()
    return s

def build_base(title, year, genre, source):
    b = title
    if year:
        b = b + " (" + str(year) + ")"
    if truthy("INCLUDE_GENRE_TAG", "1") and genre:
        b = b + " [" + genre + "]"
    if truthy("INCLUDE_SOURCE_TAG", "1") and source:
        b = b + " {" + source + "}"
    return b

def build_destination(match, src_path, output_root):
    ext = os.path.splitext(src_path)[1].lower()
    title = safe_name(match.get("title") or os.path.splitext(os.path.basename(src_path))[0])
    year = match.get("year")
    genre = safe_name(match.get("primary_genre")) if match.get("primary_genre") else None
    source = safe_name(match.get("source")) if match.get("source") else None
    base = safe_name(build_base(title, year, genre, source))
    sub = (os.getenv("MOVIE_ROOT_SUBDIR") or "").strip()
    root = output_root if not sub else os.path.join(output_root, sub)
    folder = os.path.join(root, base)
    return folder, base + ext

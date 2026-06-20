# DiscoBall

DiscoBall is a Docker-friendly post-rip/post-transcode watcher for a MakeMKV → HandBrake → library workflow. It waits until a video file is stable, identifies the movie from the file/folder name, asks metadata providers for the canonical title/year/genre, then moves the file into a clean library folder.

Default output:

```text
/output/Half Baked (1998) [Comedy] {DVD}/Half Baked (1998) [Comedy] {DVD}.mp4
```

## What was fixed in this rework

- The Python package now has the correct `src/discoball/...` structure expected by `pyproject.toml`.
- The CLI works: `watch`, `scan`, `once`, `identify`, and `imdb-index`.
- The watcher no longer contains pseudo-code or invalid indentation.
- The UI starts correctly when `UI_ENABLED=1`.
- MakeMKV-style generic files like `title_t00.mkv` use the parent folder as the title guess.
- OMDb is the primary live metadata provider.
- An optional local IMDb non-commercial dataset index can be used as a fallback provider.
- Low-confidence or unmatched files go to `_Unmatched` instead of being incorrectly filed.
- Every processed file gets a `.discoball.json` sidecar with the match, confidence, source path, and destination path.

## Important limitation

A DVD/Blu-ray rip named only `title_t00.mkv` does **not** contain enough information by itself to reliably identify a film. DiscoBall therefore expects the MakeMKV/HandBrake output folder to contain the likely title, for example:

```text
/watch/Half Baked (1998)/title_t00.mkv
```

That is the MakeMKV equivalent of giving the system a CDDB-like disc hint. With only `/watch/title_t00.mkv`, the best safe behavior is to route the file to `_Unmatched`.

## Quick start with Docker Compose

1. Copy `.env.example` to `.env`.
2. Put your OMDb key in `.env`:

```env
OMDB_API_KEY=your-key-here
```

3. Edit the host paths in `docker-compose.yml`:

```yaml
volumes:
  - /media/ZimaOS-HD/Media/Movies_Encoded:/watch
  - /media/ZimaOS-HD/Media/Library:/output
  - /media/ZimaOS-HD/AppData/discoball:/config
```

4. Start it:

```bash
docker compose up -d --build
```

5. Open the status UI:

```text
http://<zimaos-ip>:8000
```

## Recommended MakeMKV / HandBrake protocol

Use a per-disc or per-title folder name that contains the movie title and, ideally, year:

```text
/watch/Movie Title (Year)/title_t00.mkv
```

Good:

```text
/watch/Half Baked (1998)/title_t00.mkv
/watch/The Matrix (1999)/title_t00.mkv
```

Bad:

```text
/watch/title_t00.mkv
/watch/output/title_t00.mkv
```

## Test identification before moving files

```bash
docker compose run --rm discoball discoball identify "/watch/Half Baked (1998)/title_t00.mkv"
```

Single-file dry run:

```bash
docker compose run --rm discoball discoball once --dry-run "/watch/Half Baked (1998)/title_t00.mkv"
```

## Optional local IMDb fallback

OMDb is easiest and should be enough for most movie naming. If you want an IMDb-backed offline fallback, download `title.basics.tsv.gz` from IMDb's non-commercial datasets and mount that folder into the container, then build the local SQLite index:

```bash
docker compose run --rm \
  -v /path/to/imdb-datasets:/imdb \
  discoball discoball imdb-index --dataset-dir /imdb --db /config/imdb.sqlite
```

Then keep:

```env
PROVIDERS=omdb,imdb
IMDB_SQLITE_PATH=/config/imdb.sqlite
```

DiscoBall does **not** scrape imdb.com pages. It uses OMDb and optionally IMDb's published non-commercial datasets because that is more stable and less likely to break.

## Key environment variables

| Variable | Default | Purpose |
|---|---:|---|
| `WATCH_DIR` | `/watch` | Input folder watched for completed video files. |
| `OUTPUT_DIR` | `/output` | Library destination root. |
| `OMDB_API_KEY` | blank | Enables OMDb metadata lookup. |
| `PROVIDERS` | `omdb,imdb` | Metadata provider order. IMDb requires local SQLite index. |
| `STABLE_TIME_SECONDS` | `120` | Required unchanged file time before processing. |
| `CHECK_INTERVAL_SECONDS` | `30` | Stability polling interval. |
| `MIN_CONFIDENCE` | `0.64` | Below this, file goes to `_Unmatched`. |
| `MIN_VIDEO_SIZE_MB` | `50` | Skips menus, samples, and tiny extras. |
| `FILE_ACTION` | `move` | `move`, `copy`, or `hardlink`. |
| `CONFLICT_POLICY` | `suffix` | `suffix`, `skip`, or `overwrite`. |
| `NAMING_STYLE` | `discoball` | `discoball` keeps `[Genre] {DVD}` tags. `plex` omits tags from file/folder names. |
| `UI_ENABLED` | `0` | Set to `1` to enable web status UI. |

## Licensing / acknowledgements

This repository remains MIT licensed. OMDb and IMDb data have their own terms and licensing. Use those providers only in a way that complies with their terms.

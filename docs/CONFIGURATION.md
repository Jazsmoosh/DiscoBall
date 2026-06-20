# DiscoBall Configuration Reference

DiscoBall is configured through Docker environment variables. The recommended pattern is:

1. copy `.env.example` to `.env`
2. edit `.env`
3. leave `docker-compose.yml` mostly unchanged

Do not commit `.env`.

## Required variable

| Variable | Required | Example | Purpose |
|---|---:|---|---|
| `OMDB_API_KEY` | Yes for OMDb | `abc123` | Enables OMDb metadata lookup. |

Without an OMDb key, DiscoBall can still run, but live movie metadata matching will be limited.

## Host path variables

These are interpreted by Docker Compose on the host side.

| Variable | Default | Purpose |
|---|---|---|
| `DISCOBALL_WATCH_PATH` | `./watch` | Host folder mounted to `/watch`. |
| `DISCOBALL_OUTPUT_PATH` | `./output` | Host folder mounted to `/output`. |
| `DISCOBALL_CONFIG_PATH` | `./config` | Host folder mounted to `/config`. |
| `DISCOBALL_WEB_PORT` | `8000` | Host port mapped to container port `8000`. |
| `DISCOBALL_CONTAINER_NAME` | `discoball` | Docker container name. |

## Container path variables

These are normally left alone.

| Variable | Default | Purpose |
|---|---|---|
| `WATCH_DIR` | `/watch` | In-container input folder. |
| `OUTPUT_DIR` | `/output` | In-container library output folder. |
| `CONFIG_DIR` | `/config` | In-container config/data folder. |

## Watcher behavior

| Variable | Default | Purpose |
|---|---:|---|
| `STABLE_TIME_SECONDS` | `120` | File must remain unchanged for this many seconds before processing. |
| `CHECK_INTERVAL_SECONDS` | `30` | File-size polling interval. |
| `VIDEO_EXTENSIONS` | `mkv,mp4` | Comma-separated extensions to process. |
| `MIN_VIDEO_SIZE_MB` | `50` | Skip tiny files, menus, extras, samples. |

## Metadata behavior

| Variable | Default | Purpose |
|---|---|---|
| `PROVIDERS` | `omdb,imdb` | Provider order. |
| `OMDB_API_KEY` | blank | OMDb API key. |
| `IMDB_SQLITE_PATH` | `/config/imdb.sqlite` | Optional local IMDb SQLite fallback index. |
| `MIN_CONFIDENCE` | `0.64` | Matches below this route to `_Unmatched`. |

## Naming behavior

| Variable | Default | Purpose |
|---|---|---|
| `SOURCE_TAG_DEFAULT` | `DVD` | Source tag appended when source tags are enabled. |
| `INCLUDE_GENRE_TAG` | `1` | Include `[Genre]` in output names. |
| `INCLUDE_SOURCE_TAG` | `1` | Include `{DVD}` or configured source in output names. |
| `NAMING_STYLE` | `discoball` | `discoball` keeps tags; `plex` omits genre/source tags. |
| `MOVIE_ROOT_SUBDIR` | blank | Optional subfolder below `/output` for movies. |
| `TV_ROOT_SUBDIR` | blank | Reserved for TV-style organization. |
| `UNMATCHED_SUBDIR` | `_Unmatched` | Destination for uncertain matches. |

## File action behavior

| Variable | Default | Valid values | Purpose |
|---|---|---|---|
| `FILE_ACTION` | `move` | `move`, `copy`, `hardlink` | How to place files into the output library. |
| `CONFLICT_POLICY` | `suffix` | `suffix`, `skip`, `overwrite` | What to do when destination exists. |

## UI behavior

| Variable | Default | Purpose |
|---|---:|---|
| `UI_ENABLED` | `1` | Enable web dashboard. |
| `UI_PORT` | `8000` | In-container UI port. Usually do not change. |
| `DISCOBALL_WEB_PORT` | `8000` | Host-side published port. Change this to avoid host conflicts. |

## Example `.env` for a Linux server

```env
OMDB_API_KEY=your_key_here
DISCOBALL_WATCH_PATH=/srv/media/incoming
DISCOBALL_OUTPUT_PATH=/srv/media/library
DISCOBALL_CONFIG_PATH=/srv/discoball/config
DISCOBALL_WEB_PORT=8000
SOURCE_TAG_DEFAULT=DVD
PROVIDERS=omdb,imdb
UI_ENABLED=1
```

## Example `.env` for local testing

```env
OMDB_API_KEY=your_key_here
DISCOBALL_WATCH_PATH=./watch
DISCOBALL_OUTPUT_PATH=./output
DISCOBALL_CONFIG_PATH=./config
DISCOBALL_WEB_PORT=8000
SOURCE_TAG_DEFAULT=DVD
PROVIDERS=omdb,imdb
UI_ENABLED=1
```

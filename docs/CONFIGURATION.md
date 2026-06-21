# DiscoBall Configuration Reference

## Required variable

| Variable | Required | Example | Purpose |
|---|---:|---|---|
| `OMDB_API_KEY` | Yes for OMDb | `abc123` | Enables OMDb metadata lookup. |

## Host path variables

| Variable | Default | Purpose |
|---|---|---|
| `DISCOBALL_WATCH_PATH` | `./watch` | Host folder mounted to `/watch`. |
| `DISCOBALL_OUTPUT_PATH` | `./output` | Host folder mounted to `/output`. |
| `DISCOBALL_CONFIG_PATH` | `./config` | Host folder mounted to `/config`. |
| `DISCOBALL_WEB_PORT` | `8000` | Host port mapped to container port `8000`. |
| `DISCOBALL_CONTAINER_NAME` | `discoball` | Docker container name. |

## UI behavior

| Variable | Default | Purpose |
|---|---:|---|
| `UI_ENABLED` | `1` | Enable web dashboard. |
| `UI_PORT` | `8000` | In-container UI port. Usually do not change. |

Publishing `8000` without `UI_ENABLED=1` can create a running watcher container with no web UI listener.

## ZimaOS example

```env
OMDB_API_KEY=your_key_here
DISCOBALL_WATCH_PATH=/DATA/Media/HandBrake/output
DISCOBALL_OUTPUT_PATH=/DATA/Media/Library
DISCOBALL_CONFIG_PATH=/DATA/AppData/discoball
DISCOBALL_WEB_PORT=18000
UI_ENABLED=1
UI_PORT=8000
PROVIDERS=omdb,imdb
SOURCE_TAG_DEFAULT=DVD
```
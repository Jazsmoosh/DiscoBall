# DiscoBall

<!-- DISCOBALL-ZIMAOS-PIPELINE:START -->

## Recommended ZimaOS workflow

For the smoothest out-of-box workflow on ZimaOS, use:

`	ext
MakeMKV -> HandBrake -> Discoball
`

Recommended Docker path flow:

`	ext
MakeMKV:
  /DATA/Media/MakeMKV/output  -> /output

HandBrake:
  /DATA/Media/MakeMKV/output   -> /watch
  /DATA/Media/HandBrake/output -> /output

Discoball:
  /DATA/Media/HandBrake/output -> /watch
  /DATA/Media/Library          -> /output
`

Discoball should watch completed HandBrake output, not raw MakeMKV output, when HandBrake is part of the workflow.

Full ZimaOS setup guide:

`	ext
docs/ZIMAOS_MEDIA_PIPELINE.md
`

Example compose file:

`	ext
examples/zimaos-media-pipeline.compose.yml
`

<!-- DISCOBALL-ZIMAOS-PIPELINE:END -->

DiscoBall is a Docker-friendly post-process watcher for MakeMKV-style media workflows. It watches an ingest folder, waits for a video file to stop changing, identifies the movie with metadata providers such as OMDb, and moves or copies the completed file into a clean library structure.

It is designed to be portable across any Docker host: Linux server, NAS, homelab box, Docker Desktop, Proxmox LXC/VM, Unraid, Synology-style Docker environments, CasaOS, ZimaOS, or a plain Ubuntu/Debian box.

> DiscoBall is not a ripper, decryptor, or media source. It only organizes local video files that already exist in a folder you provide.

## What it does

Input example:

```text
/watch/Cast Away (2000)/F4_t00.mkv
```

Output example:

```text
/output/Cast Away (2000) [Adventure] {DVD}/Cast Away (2000) [Adventure] {DVD}.mkv
```

Why the parent folder matters:

MakeMKV often creates generic filenames such as `title_t00.mkv`, `F4_t00.mkv`, `A1_t00.mkv`, or `VTS_03_1.mkv`. Those names do not contain enough information to identify a movie reliably. DiscoBall treats those names as generic and uses the nearest meaningful parent folder, such as `Cast Away (2000)`, as the metadata hint.

## Features

- Portable Docker Compose deployment
- OMDb metadata lookup
- Optional local IMDb non-commercial dataset fallback
- Generic MakeMKV filename detection
- File-size stability wait before processing
- Configurable move/copy/hardlink behavior
- Safe `_Unmatched` routing for low-confidence matches
- JSON sidecar audit file for each processed item
- Cyberdream web dashboard
- CLI commands for watch, scan, identify, and one-time processing
- No external frontend assets, CDN, telemetry, or JavaScript framework

## Quick start

### 1. Clone

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
```

### 2. Create `.env`

```bash
cp .env.example .env
nano .env
```

At minimum, set:

```env
OMDB_API_KEY=your_omdb_key_here
```

Do not commit `.env`.

### 3. Choose host folders

DiscoBall only needs three folders:

| Purpose | Container path | Example host path |
|---|---|---|
| Ingest/watch folder | `/watch` | `/srv/media/incoming` |
| Library output folder | `/output` | `/srv/media/library` |
| App config/data folder | `/config` | `/srv/discoball/config` |

Set the host paths in `.env`:

```env
DISCOBALL_WATCH_PATH=/srv/media/incoming
DISCOBALL_OUTPUT_PATH=/srv/media/library
DISCOBALL_CONFIG_PATH=/srv/discoball/config
DISCOBALL_WEB_PORT=8000
```

For local testing on any Docker machine, the defaults can be relative folders:

```env
DISCOBALL_WATCH_PATH=./watch
DISCOBALL_OUTPUT_PATH=./output
DISCOBALL_CONFIG_PATH=./config
DISCOBALL_WEB_PORT=8000
```

### 4. Start

```bash
docker compose up -d --build
```

### 5. Open the dashboard

```text
http://<docker-host-ip>:8000
```

If you changed `DISCOBALL_WEB_PORT`, use that host port instead.

## Recommended MakeMKV-style workflow

Configure your ripper/transcoder to output into a meaningful per-title folder:

```text
Incoming Root/Movie Title (Year)/generic_file_name.mkv
```

Examples:

```text
/srv/media/incoming/Cast Away (2000)/F4_t00.mkv
/srv/media/incoming/Se7en (1995)/A1_t00.mkv
/srv/media/incoming/The Matrix (1999)/title_t00.mkv
```

Avoid:

```text
/srv/media/incoming/title_t00.mkv
/srv/media/incoming/output/F4_t00.mkv
```

DiscoBall can normalize generic file names, but it still needs a meaningful folder hint.

## CLI usage

Show help:

```bash
docker compose run --rm discoball discoball --help
```

Identify a file without moving it:

```bash
docker compose run --rm discoball discoball identify "/watch/Cast Away (2000)/F4_t00.mkv"
```

Process one file:

```bash
docker compose run --rm discoball discoball once "/watch/Cast Away (2000)/F4_t00.mkv"
```

Dry-run one file:

```bash
docker compose run --rm discoball discoball once --dry-run "/watch/Cast Away (2000)/F4_t00.mkv"
```

Run a one-time scan of the watch folder:

```bash
docker compose run --rm discoball discoball scan
```

Run the long-lived watcher:

```bash
docker compose up -d
```

## Documentation

- [Install Guide](docs/INSTALL.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [Workflow Guide](docs/WORKFLOW.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Technical SOP](docs/SOP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Metadata providers

### OMDb

OMDb is the default live metadata provider. Put the API key in `.env`:

```env
OMDB_API_KEY=your_omdb_key_here
```

### Optional IMDb local fallback

DiscoBall can optionally build a local SQLite index from IMDb non-commercial dataset files.

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

DiscoBall does not scrape IMDb pages.

## License and acknowledgements

DiscoBall is released under the MIT License. See [LICENSE](LICENSE).

OMDb, IMDb datasets, MakeMKV, Docker, and any media-library tools you pair with DiscoBall have their own terms and licensing. Use each service and dataset according to its terms.

## Legal note

DiscoBall does not provide, decrypt, bypass, download, or distribute media. It is a local file organization tool. Users are responsible for ensuring they have the right to process any media files they place into the watch folder and for complying with local law.


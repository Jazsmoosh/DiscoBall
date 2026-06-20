# DiscoBall Install Guide

This guide is intentionally Docker-host agnostic. It works for a normal Linux server, NAS, homelab machine, Docker Desktop, VM, LXC, Unraid-style Docker host, CasaOS, ZimaOS, or any environment that can run Docker Compose.

## Requirements

- Docker Engine or Docker Desktop
- Docker Compose plugin
- Git
- An OMDb API key
- Three host folders:
  - watch/ingest folder
  - library/output folder
  - config/data folder

## Folder model

DiscoBall uses fixed container paths:

```text
/watch   = input folder watched by DiscoBall
/output  = renamed library output folder
/config  = app config/data folder
```

You choose where those paths live on the Docker host.

Example Linux host layout:

```text
/srv/media/incoming
/srv/media/library
/srv/discoball/config
```

Example local test layout:

```text
./watch
./output
./config
```

## Install from source

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
cp .env.example .env
```

Edit `.env`:

```bash
nano .env
```

Minimum required setting:

```env
OMDB_API_KEY=your_omdb_key_here
```

Recommended host path settings:

```env
DISCOBALL_WATCH_PATH=/srv/media/incoming
DISCOBALL_OUTPUT_PATH=/srv/media/library
DISCOBALL_CONFIG_PATH=/srv/discoball/config
DISCOBALL_WEB_PORT=8000
```

Create host folders:

```bash
mkdir -p "$DISCOBALL_WATCH_PATH" "$DISCOBALL_OUTPUT_PATH" "$DISCOBALL_CONFIG_PATH"
```

If the folders are shared with another container such as MakeMKV, ensure both containers can write to the required paths.

For a simple single-user homelab test:

```bash
chmod -R a+rwx "$DISCOBALL_WATCH_PATH" "$DISCOBALL_OUTPUT_PATH" "$DISCOBALL_CONFIG_PATH"
```

For a production-ish system, use a shared group or ACLs instead of world-writable permissions.

## Start

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
docker compose logs --tail=100 discoball
```

Expected log line:

```text
watching: /watch
```

## Open dashboard

From the Docker host:

```bash
curl -fsS http://127.0.0.1:8000/api/status
```

From another device on the network:

```text
http://<docker-host-ip>:8000
```

If you set `DISCOBALL_WEB_PORT=18000`, use:

```text
http://<docker-host-ip>:18000
```

## Test metadata lookup

```bash
docker compose run --rm discoball discoball identify "/watch/Cast Away (2000)/F4_t00.mkv"
```

This test path does not need the file to exist for title parsing and metadata lookup; it validates whether the folder/name hint can identify the movie.

## Test one file

Put a real MKV at:

```text
<watch-host-path>/Cast Away (2000)/F4_t00.mkv
```

Then run:

```bash
docker compose run --rm discoball discoball once "/watch/Cast Away (2000)/F4_t00.mkv"
```

Expected result:

```text
<output-host-path>/Cast Away (2000) [Adventure] {DVD}/Cast Away (2000) [Adventure] {DVD}.mkv
```

## Update an existing source install

```bash
cd /path/to/DiscoBall
git pull --ff-only origin main
docker compose up -d --build
```

If you have local Compose path edits, back up your files before pulling:

```bash
mkdir -p .discoball-backups
cp docker-compose.yml .discoball-backups/docker-compose.yml.$(date +%Y%m%d-%H%M%S).bak
cp .env .discoball-backups/.env.$(date +%Y%m%d-%H%M%S).bak 2>/dev/null || true
```

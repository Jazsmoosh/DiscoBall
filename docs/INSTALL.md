# DiscoBall Install Guide

## Requirements

- Docker Engine or Docker Desktop
- Docker Compose plugin for Compose installs
- Git for source installs
- An OMDb API key
- A watch/input folder
- A library/output folder
- A config/data folder

## Folder model

```text
/watch   = input folder watched by DiscoBall
/output  = renamed library output folder
/config  = app config/data folder
```

## Fast ZimaOS install

Use this when MakeMKV and HandBrake are already installed and HandBrake outputs to `/DATA/Media/HandBrake/output`.

```bash
curl -fsSL https://raw.githubusercontent.com/Jazsmoosh/DiscoBall/main/scripts/install-zimaos-discoball.sh -o /tmp/install-zimaos-discoball.sh
chmod +x /tmp/install-zimaos-discoball.sh
sudo /tmp/install-zimaos-discoball.sh
```

The installer prompts for your OMDb API key before starting the container.

## Docker Compose install

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
cp .env.example .env
nano .env
```

Minimum required setting:

```env
OMDB_API_KEY=your_omdb_key_here
```

Start:

```bash
docker compose up -d --build
```

Health check:

```bash
curl -fsS "http://127.0.0.1:${DISCOBALL_WEB_PORT:-8000}/healthz"
```

## Direct Docker install

```bash
docker run -d \
  --name discoball \
  --restart unless-stopped \
  -p 18000:8000 \
  -e UI_ENABLED=1 \
  -e UI_PORT=8000 \
  -e OMDB_API_KEY="your_omdb_key_here" \
  -v /srv/media/incoming:/watch:rw \
  -v /srv/media/library:/output:rw \
  -v /srv/discoball/config:/config:rw \
  ghcr.io/jazsmoosh/discoball:latest \
  discoball watch
```
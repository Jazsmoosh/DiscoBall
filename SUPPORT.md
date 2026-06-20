# Support

## Before opening an issue

Run:

```bash
docker compose ps
docker compose logs --tail=150 discoball
docker compose config
```

Redact secrets before posting output.

## Include this information

- Docker host OS/platform
- Docker version
- Docker Compose version
- install method: source build or image pull
- sanitized `docker-compose.yml`
- sanitized `.env` without API keys
- sample input path
- expected output path
- actual output path
- `discoball identify` output for the same file
- whether the file landed in `_Unmatched`

## Useful commands

Identify without moving:

```bash
docker compose run --rm discoball discoball identify "/watch/Movie Title (Year)/file.mkv"
```

One-file dry run:

```bash
docker compose run --rm discoball discoball once --dry-run "/watch/Movie Title (Year)/file.mkv"
```

Follow logs:

```bash
docker compose logs -f discoball
```

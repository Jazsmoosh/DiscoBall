# DiscoBall Technical SOP

## 1. Purpose

This SOP provides a repeatable process to deploy, validate, update, and troubleshoot DiscoBall on any Docker host.

## 2. Standard deployment layout

Container paths:

```text
/watch
/output
/config
```

Host paths are site-specific and should be set in `.env`.

Example:

```env
DISCOBALL_WATCH_PATH=/srv/media/incoming
DISCOBALL_OUTPUT_PATH=/srv/media/library
DISCOBALL_CONFIG_PATH=/srv/discoball/config
DISCOBALL_WEB_PORT=8000
```

## 3. Initial deployment

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
cp .env.example .env
nano .env
```

Set:

```env
OMDB_API_KEY=your_omdb_key_here
```

Create folders:

```bash
mkdir -p "$DISCOBALL_WATCH_PATH" "$DISCOBALL_OUTPUT_PATH" "$DISCOBALL_CONFIG_PATH"
```

Start:

```bash
docker compose up -d --build
```

Validate:

```bash
docker compose ps
docker compose logs --tail=100 discoball
curl -fsS http://127.0.0.1:${DISCOBALL_WEB_PORT:-8000}/api/status
```

## 4. Functional validation

Run identify:

```bash
docker compose run --rm discoball discoball identify "/watch/Cast Away (2000)/F4_t00.mkv"
```

Expected:

- query: `Cast Away`
- year: `2000`
- provider: `omdb`
- confidence: high

## 5. Operational workflow

1. Create an ingest subfolder named `Movie Title (Year)`.
2. Send MakeMKV/transcoder output into that subfolder.
3. Allow the file to finish writing.
4. DiscoBall waits for stability.
5. DiscoBall performs metadata lookup.
6. DiscoBall files the movie into the output library.
7. Review `_Unmatched` periodically.

## 6. Update procedure

Back up local configuration:

```bash
mkdir -p .discoball-backups
cp docker-compose.yml .discoball-backups/docker-compose.yml.$(date +%Y%m%d-%H%M%S).bak
cp .env .discoball-backups/.env.$(date +%Y%m%d-%H%M%S).bak 2>/dev/null || true
```

Pull:

```bash
git fetch origin
git pull --ff-only origin main
```

If blocked by local Compose edits:

```bash
git stash push -m "local docker-compose override" docker-compose.yml
git pull --ff-only origin main
git stash pop
```

Rebuild:

```bash
docker compose down --remove-orphans
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 discoball
```

Validate UI/API:

```bash
curl -fsS http://127.0.0.1:${DISCOBALL_WEB_PORT:-8000}/api/status
```

## 7. Release procedure for maintainers

Confirm clean working tree:

```bash
git status
git log --oneline -5
```

Confirm secrets are not tracked:

```bash
git ls-files .env
git log --all -- .env
```

Tag:

```bash
git tag -a v0.1.0 -m "DiscoBall v0.1.0"
git push origin v0.1.0
```

Draft a GitHub release using the tag.

## 8. Rollback procedure

List recent commits:

```bash
git log --oneline -5
```

Revert latest code commit:

```bash
git revert HEAD
docker compose up -d --build
```

Or restore a backed-up Compose file:

```bash
cp .discoball-backups/docker-compose.yml.YYYYMMDD-HHMMSS.bak docker-compose.yml
docker compose up -d --build
```

## 9. Support data collection

Collect:

```bash
docker compose config
docker compose ps
docker compose logs --tail=150 discoball
git status
git log --oneline -5
```

Redact:

- OMDb key
- hostnames if sensitive
- private share paths if sensitive
- media names if sensitive

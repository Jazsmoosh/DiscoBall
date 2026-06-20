# DiscoBall Troubleshooting

## Quick health commands

```bash
docker compose ps
docker compose logs --tail=150 discoball
curl -fsS http://127.0.0.1:${DISCOBALL_WEB_PORT:-8000}/api/status
```

## Browser cannot connect

If you are using a browser on another machine, do not use `127.0.0.1` unless DiscoBall runs on that same machine.

Use:

```text
http://<docker-host-ip>:<DISCOBALL_WEB_PORT>
```

Example:

```text
http://192.168.1.50:8000
```

## Host port conflict

If port `8000` is already in use, change only the host port:

```env
DISCOBALL_WEB_PORT=18000
```

Keep:

```env
UI_PORT=8000
```

Then rebuild/restart:

```bash
docker compose up -d --build
```

Open:

```text
http://<docker-host-ip>:18000
```

## MakeMKV or another container cannot write to the watch folder

This is a host volume permission issue.

Check the path mounted into that container and test writing inside the container.

Example:

```bash
docker exec -it MakeMKV sh -lc 'set -eux; mkdir -p /output/_write_test; touch /output/_write_test/test.txt; rm -rf /output/_write_test'
```

For a simple local homelab test:

```bash
sudo chmod -R a+rwx /path/to/watch
sudo chmod -R a+rwx /path/to/output
```

For a cleaner multi-user setup, use a shared group or ACLs.

## File went to `_Unmatched`

Run identify manually:

```bash
docker compose run --rm discoball discoball identify "/watch/Movie Title (Year)/file.mkv"
```

Check:

- Does the query look right?
- Is the year detected?
- Is OMDb returning a match?
- Is confidence above `MIN_CONFIDENCE`?

## OMDb check without printing the key

```bash
docker compose run --rm discoball sh -lc 'test -n "$OMDB_API_KEY" && echo "OMDb key present" || echo "OMDb key missing"'
```

Functional test:

```bash
docker compose run --rm discoball sh -lc 'python - <<PY
import os, requests
key=os.getenv("OMDB_API_KEY")
r=requests.get("https://www.omdbapi.com/", params={"apikey":key,"t":"Cast Away","y":"2000"}, timeout=15)
j=r.json()
print({"Response": j.get("Response"), "Title": j.get("Title"), "Year": j.get("Year"), "Error": j.get("Error")})
PY'
```

Expected:

```text
{'Response': 'True', 'Title': 'Cast Away', 'Year': '2000', 'Error': None}
```

## Compose YAML error

Validate Compose:

```bash
docker compose config
```

If this fails, fix `docker-compose.yml` before rebuilding.

## Docker Buildx permission error

Some appliance-style Docker hosts set unusual Docker config paths. Bypass with a per-user Docker config:

```bash
mkdir -p "$HOME/.docker/buildx"
export DOCKER_CONFIG="$HOME/.docker"
docker compose up -d --build
```

To persist:

```bash
echo 'export DOCKER_CONFIG="$HOME/.docker"' >> ~/.bashrc
```

## Local `docker-compose.yml` edits block git pull

Back up first:

```bash
mkdir -p .discoball-backups
cp docker-compose.yml .discoball-backups/docker-compose.yml.$(date +%Y%m%d-%H%M%S).bak
```

Then stash local Compose edits:

```bash
git stash push -m "local docker-compose override" docker-compose.yml
git pull --ff-only origin main
git stash pop
```

Review the resulting `docker-compose.yml` before rebuilding.

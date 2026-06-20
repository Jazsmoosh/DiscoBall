---
name: Bug report
about: Report something that is not working as expected
title: "[Bug]: "
labels: bug
assignees: ''
---

## Summary

What happened?

## Environment

- Docker host OS/platform:
- Docker version:
- Docker Compose version:
- Install method: source build / image pull
- DiscoBall commit or version:

## Sanitized configuration

Paste `docker-compose.yml` and relevant `.env` values. Remove API keys.

```yaml
# docker-compose.yml
```

```env
# .env, redacted
OMDB_API_KEY=REDACTED
```

## Input path

```text
/watch/Movie Title (Year)/file.mkv
```

## Expected output

```text
/output/Movie Title (Year) [Genre] {DVD}/Movie Title (Year) [Genre] {DVD}.mkv
```

## Actual output

```text

```

## Logs

```bash
docker compose logs --tail=150 discoball
```

```text
paste logs here
```

## Identify output

```bash
docker compose run --rm discoball discoball identify "/watch/Movie Title (Year)/file.mkv"
```

```text
paste output here
```

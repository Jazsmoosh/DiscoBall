# Security Policy

## Supported versions

DiscoBall is early-stage software. Security fixes are expected to land on `main` until versioned releases are formalized.

## Reporting a vulnerability

Please open a private security advisory on GitHub when possible. If that is unavailable, open an issue with minimal reproduction detail and avoid posting secrets, API keys, private paths, or media names.

## Secrets handling

Do not commit:

- `.env`
- OMDb API keys
- local SQLite databases
- media files
- private host paths if sensitive
- backup folders

Use `.env.example` for placeholders only.

## Container security notes

DiscoBall needs write access to `/watch`, `/output`, and `/config` only.

Avoid mounting broader host paths than needed. Prefer narrow bind mounts such as:

```yaml
volumes:
  - /srv/media/incoming:/watch
  - /srv/media/library:/output
  - /srv/discoball/config:/config
```

Do not mount `/`, `/home`, `/var/run/docker.sock`, or other sensitive host paths into DiscoBall.

## Media/legal note

DiscoBall does not rip, decrypt, download, or distribute media. It is a local organization tool. Users are responsible for lawful use and for ensuring they have rights to process the files they place in the watch folder.

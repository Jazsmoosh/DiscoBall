# DiscoBall Architecture

## Runtime components

DiscoBall is a Python package installed into a container image. The container usually runs:

```text
discoball watch
```

Main modules:

| Module | Purpose |
|---|---|
| `main.py` | CLI entry point. |
| `config.py` | Environment/config loading. |
| `watcher.py` | Filesystem watcher and stability wait. |
| `guess.py` | Path/name title hint extraction. |
| `providers/omdb.py` | OMDb metadata provider. |
| `providers/imdb_dataset.py` | Optional local IMDb dataset provider. |
| `providers/registry.py` | Provider ordering and match selection. |
| `naming.py` | Destination folder/file construction. |
| `processor.py` | Move/copy/hardlink and sidecar writing. |
| `state.py` | In-memory status snapshot for UI. |
| `ui.py` | Dependency-free web dashboard. |

## Data flow

```text
/watch/Movie Title (Year)/generic_name.mkv
    -> stability wait
    -> title guess
    -> metadata lookup
    -> confidence check
    -> naming policy
    -> move/copy/hardlink
    -> .discoball.json sidecar
```

## Match safety

DiscoBall prefers false negatives over false positives. If a match is low-confidence, it routes to `_Unmatched` rather than filing the media incorrectly.

## Sidecar structure

Each processed file receives a JSON sidecar containing source path, destination path, matched metadata, provider, confidence, and related details. This makes processing auditable and reversible by a human.

## UI design

The web UI is intentionally small and self-contained:

- no CDN
- no external web fonts
- no framework
- no telemetry
- polls `/api/status`

## Container portability

The application assumes only three mounted folders:

```text
/watch
/output
/config
```

Everything else is configured through environment variables.

# Disco Ball
Docker-friendly post-transcode tagger/renamer.

## Naming schema (library root)
Example:
Half Baked (1998) [Comedy] {DVD}

- Title + Year from metadata (OMDb preferred)
- [Genre] = primary genre (first OMDb genre)
- {Source} defaults to DVD on your system

Output example:
/output/Half Baked (1998) [Comedy] {DVD}/Half Baked (1998) [Comedy] {DVD}.mp4

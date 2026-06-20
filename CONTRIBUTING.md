# Contributing to DiscoBall

Thanks for checking out DiscoBall.

## Good contributions

Helpful areas:

- Docker portability improvements
- metadata matching improvements
- clearer documentation
- tests for weird MakeMKV filenames
- safer unmatched handling
- UI clarity
- provider abstraction improvements

## Development setup

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Run tests

```bash
pytest
```

If pytest is not installed:

```bash
pip install pytest
pytest
```

## Commit hygiene

Do not commit:

- `.env`
- API keys
- local media files
- generated SQLite files
- `.discoball-backups/`
- large test videos

Use targeted adds:

```bash
git add README.md docs/ src/discoball/ tests/
```

Avoid:

```bash
git add -A
```

unless you have reviewed all new files.

## Pull request checklist

Before submitting:

```bash
git status
python -m compileall src
pytest
```

Also run:

```bash
git ls-files .env
```

Expected: no output.

## Project positioning

DiscoBall is a post-processing organizer. It is not a ripping, decryption, download, or piracy tool. Keep issues, docs, and examples framed around legitimate local media organization.

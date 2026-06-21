# ZimaOS Media Pipeline: MakeMKV to HandBrake to DiscoBall

Recommended workflow:

```text
Disc -> MakeMKV raw rip -> HandBrake completed encode -> DiscoBall organized library
```

## Folder layout

```text
/DATA/AppData/makemkv
/DATA/AppData/handbrake/config
/DATA/AppData/discoball

/DATA/Media/MakeMKV/output
/DATA/Media/HandBrake/output
/DATA/Media/Library
```

ZimaOS Files may show `/ZimaOS-HD/Media/...`, but Docker host paths are normally `/DATA/Media/...` over SSH.

## Ports

```text
MakeMKV    host 6220  -> container 5800
HandBrake  host 15800 -> container 5800
DiscoBall  host 18000 -> container 8000
```

## MakeMKV

```text
/DATA/AppData/makemkv       -> /config
/DATA/Media                 -> /storage
/DATA/Media/MakeMKV/output  -> /output
```

MakeMKV usually needs both the optical block device and matching SCSI generic device:

```text
/dev/sr0 -> /dev/sr0
/dev/sg0 -> /dev/sg0
```

## HandBrake

```text
/DATA/AppData/handbrake/config  -> /config
/DATA/Media                     -> /storage
/DATA/Media/MakeMKV/output      -> /watch
/DATA/Media/HandBrake/output    -> /output
```

## DiscoBall

```text
/DATA/AppData/discoball       -> /config
/DATA/Media/HandBrake/output  -> /watch
/DATA/Media/Library           -> /output
```

Required direct Docker settings:

```env
UI_ENABLED=1
UI_PORT=8000
OMDB_API_KEY=your_key_here
```

Install:

```bash
curl -fsSL https://raw.githubusercontent.com/Jazsmoosh/DiscoBall/main/scripts/install-zimaos-discoball.sh -o /tmp/install-zimaos-discoball.sh
chmod +x /tmp/install-zimaos-discoball.sh
sudo /tmp/install-zimaos-discoball.sh
```
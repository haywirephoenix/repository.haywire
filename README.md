# repository.haywire

A Kodi repository for haywirephoenix's add-ons:

| Add-on | |
|---|---|
| `plugin.video.floppy` | Floppy |
| `script.tmdbhelper.sync.floppy` | TMDbHelper Sync - Floppy (Installer): install this one, it brings the sync module |
| `script.module.tmdbhelper.sync.floppy` | TMDbHelper Sync - Floppy |
| `plugin.video.ultra.player` | Ultra Player: plays titles from Stremio and Nuvio add-ons |
| `plugin.video.torrest` | Torrest fork: buffering and download status for skins (all platforms' binaries) |

## Install

1. Download the repository add-on:
   [repository.haywire-1.0.1.zip](https://raw.githubusercontent.com/haywirephoenix/repository.haywire/main/zips/repository.haywire/repository.haywire-1.0.1.zip)
2. In Kodi: Add-ons > Install from zip file, pick it (allow unknown sources if asked).
3. Install the add-ons from Add-ons > Install from repository > haywire repository. Kodi
   updates them from here.

## How it's published

`zips/` is what Kodi reads: `addons.xml` (+ `.md5`), and per add-on its zips (the last two
versions, each with a `.sha256`) and its icon and fanart.

Each add-on's repository has a small workflow that calls `.github/workflows/publish-addon.yml`
here whenever its `addon.xml` version changes (or by hand). That builds the zip, adds it with
`tools/update_repo.py`, and pushes. The add-on repositories need a secret,
`REPOSITORY_HAYWIRE_TOKEN`: a fine-grained token with Contents read and write on this
repository only.

The repository add-on itself (`repository.haywire/`) is published the same way by
`.github/workflows/publish-repository.yml` here when its `addon.xml` version changes; it also
points the install link above at the new zip.

By hand:

    python tools/update_repo.py add path/to/plugin.video.x-1.2.3.zip
    python tools/update_repo.py pack repository.haywire     # after changing the repository add-on
    python -m unittest discover tests

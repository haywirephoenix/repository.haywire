# repository.haywire

A Kodi repository for haywirephoenix's add-ons:

| Add-on | |
|---|---|
| `plugin.video.tally` | Tally: watched status, resume points and watchlists in a local database (no host required) |
| `script.tmdbhelper.sync.tally` | TMDbHelper Sync - Tally (Installer): handy installer for the sync module to manage it from your addons page |
| `script.module.tmdbhelper.sync.tally` | TMDbHelper Sync - Tally: Sync module for TMDB Helper |
| `plugin.video.ultra.player` | Ultra Player: plays movies and episodes from customizable plugin sources or Stremio/Nuvio addons : plays the best stream or the one you pick, hands torrents to a torrent player add-on (Torrest recommended, picked automatically when installed), and plays downloads, library copies and torrents Torrest still has first, without asking the sources. Works as a player path for skins, TMDb Helper and other add-ons; Download saves a title for later |
| `plugin.video.torrest` | Torrest fork: torrent streaming with every platform's binary, including a webOS build for LG TVs. Reports buffering and download status to skins (a skin can draw its own loading screen and OSD, and cancel a play); cleans up after watching (delete when stopped near the start or watched to the end, automatically or after asking; keep season packs; pause finished torrents so nothing seeds in the background); keeps public trackers up to date; buffers the start and end of a file in parallel, and skips buffering for downloaded files; downloads without playing |
| `plugin.video.floppy` | Floppy: Companion sync addon for [Floppy](https://github.com/dannyvfilms/Floppy) self-hosted media tracker |
| `script.tmdbhelper.sync.floppy` | TMDbHelper Sync - Floppy (Installer): handy installer for the sync module to manage it from your addons page |
| `script.module.tmdbhelper.sync.floppy` | TMDbHelper Sync - Floppy: Sync module for TMDB Helper |


## Install

### Option 1 – Install from zip

1. Download the repository add-on:  
   [repository.haywire-1.0.1.zip](https://raw.githubusercontent.com/haywirephoenix/repository.haywire/main/zips/repository.haywire/repository.haywire-1.0.1.zip)
2. In Kodi go to **Add-ons → Install from zip file** and select the downloaded zip  
   (enable *Unknown sources* if prompted).
3. Then go to **Add-ons → Install from repository → haywire repository** and install the add-ons you want.  
   Kodi will keep them updated from here.

### Option 2 – Add as a File Manager source

1. In Kodi go to **File Manager → Add source**.
2. Enter this URL exactly:  
   `https://haywirephoenix.github.io/repository.haywire/`
3. Give it a name (e.g. `haywire`) and confirm.
4. Go to **Add-ons → Install from zip file**, choose the source you just added, open the `repository.haywire` folder and install the latest `repository.haywire-*.zip`.
5. After the repository is installed, go to **Install from repository → haywire repository** to install the individual add-ons.

"""Maintains the Kodi repository in zips/ (what repository.haywire's addon.xml points Kodi at).

    python tools/update_repo.py add <addon zip> [...]   add (or replace) add-on zips
    python tools/update_repo.py pack <add-on folder>    zip a folder (the repository add-on itself) and add it
    python tools/update_repo.py index                   just rebuild addons.xml / addons.xml.md5
    python tools/update_repo.py has <id> <version>      exit 0 if that version is already published

Layout, as Kodi reads it (datadir zips/, hashes sha256):

    zips/addons.xml, zips/addons.xml.md5      every add-on's addon.xml (its newest version)
    zips/<id>/<id>-<version>.zip              the add-on (one top folder, <id>/), KEEP versions kept
    zips/<id>/<id>-<version>.zip.sha256       its hash, which Kodi checks
    zips/<id>/<asset>                          its icon / fanart / ... (addon.xml <assets>), for
                                              Kodi's add-on browser
"""
import hashlib
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIPS = os.path.join(ROOT, "zips")
KEEP = 2
ZIP_NAME = re.compile(r"^(?P<id>.+)-(?P<version>\d[^/]*)\.zip$")


def version_key(version):
    """Kodi-ish ordering: numbers compare as numbers, a suffix (~beta1) sorts before none."""
    main, _, suffix = version.partition("~")
    return [int(p) if p.isdigit() else p for p in re.split(r"[.\-]", main)], suffix == "", suffix


def read_addon_xml(zip_path):
    """(id, version, addon.xml text, root element) from an add-on zip's <id>/addon.xml."""
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.count("/") == 1 and n.endswith("/addon.xml")]
        if len(names) != 1:
            raise ValueError("{}: needs exactly one <id>/addon.xml at its top, found {}".format(zip_path, names))
        text = z.read(names[0]).decode("utf-8")
    root = ET.fromstring(text)
    addon_id, version = root.get("id"), root.get("version")
    if not addon_id or not version or names[0] != addon_id + "/addon.xml":
        raise ValueError("{}: its addon.xml id / version / folder don't match".format(zip_path))
    return addon_id, version, text, root


def assets(root):
    """The asset paths an addon.xml lists (icon, fanart, banner, screenshots...)."""
    block = root.find("extension[@point='xbmc.addon.metadata']/assets")
    return [el.text.strip() for el in (block if block is not None else []) if el.text and el.text.strip()]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def published(zips=ZIPS):
    """{id: [versions, newest first]}."""
    out = {}
    for addon_id in sorted(os.listdir(zips)) if os.path.isdir(zips) else []:
        folder = os.path.join(zips, addon_id)
        if not os.path.isdir(folder):
            continue
        versions = [m.group("version") for m in map(ZIP_NAME.match, os.listdir(folder))
                    if m and m.group("id") == addon_id]
        if versions:
            out[addon_id] = sorted(versions, key=version_key, reverse=True)
    return out


def add(zip_path, zips=ZIPS):
    """Copies an add-on zip in, with its hash and assets; prunes old versions. Returns (id, version)."""
    addon_id, version, _, root = read_addon_xml(zip_path)
    folder = os.path.join(zips, addon_id)
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "{}-{}.zip".format(addon_id, version))
    with open(zip_path, "rb") as src, open(target, "wb") as dst:
        dst.write(src.read())
    with open(target + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write(sha256(target) + "\n")
    with zipfile.ZipFile(target) as z:
        for asset in assets(root):
            member = "{}/{}".format(addon_id, asset)
            if member in z.namelist():
                out = os.path.join(folder, *asset.split("/"))
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "wb") as f:
                    f.write(z.read(member))
    for old in published(zips).get(addon_id, [])[KEEP:]:
        for suffix in (".zip", ".zip.sha256"):
            path = os.path.join(folder, "{}-{}{}".format(addon_id, old, suffix))
            if os.path.exists(path):
                os.remove(path)
    return addon_id, version


def pack(folder, zips=ZIPS):
    """Zips an add-on folder as <id>/... (skipping VCS and cache files) and adds it."""
    folder = os.path.abspath(folder)
    addon_id = os.path.basename(folder)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(folder):
            dirs[:] = sorted(d for d in dirs if d not in (".git", ".github", "__pycache__"))
            for name in sorted(files):
                if name.endswith((".pyc", ".pyo")):
                    continue
                path = os.path.join(base, name)
                z.write(path, "{}/{}".format(addon_id, os.path.relpath(path, folder).replace(os.sep, "/")))
    tmp = os.path.join(zips, ".pack.zip")
    os.makedirs(zips, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(buffer.getvalue())
    try:
        return add(tmp, zips)
    finally:
        os.remove(tmp)


def index(zips=ZIPS):
    """Rebuilds addons.xml (each add-on's newest addon.xml) and its md5."""
    parts = []
    for addon_id, versions in published(zips).items():
        _, _, text, _ = read_addon_xml(os.path.join(zips, addon_id, "{}-{}.zip".format(addon_id, versions[0])))
        text = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", text).strip()
        parts.append(text)
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n{}\n</addons>\n'.format("\n".join(parts))
    ET.fromstring(xml.encode("utf-8"))  # well-formed, or stop before publishing it
    path = os.path.join(zips, "addons.xml")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    with open(path + ".md5", "w", encoding="utf-8", newline="\n") as f:
        f.write(hashlib.md5(xml.encode("utf-8")).hexdigest())
    return sorted(published(zips))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    command, args = argv[1], argv[2:]
    if command == "has":
        return 0 if args[1] in published().get(args[0], []) else 1
    if command == "add":
        for path in args:
            print("added {} {}".format(*add(path)))
    elif command == "pack":
        for path in args:
            print("packed {} {}".format(*pack(path)))
    elif command != "index":
        print(__doc__)
        return 2
    print("addons.xml: " + ", ".join(index()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

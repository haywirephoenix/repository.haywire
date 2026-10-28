#!/usr/bin/env python3
"""Generate simple Apache-style index.html files that Kodi can parse."""

import os
from pathlib import Path
from datetime import datetime

def human_size(num: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if abs(num) < 1024.0:
            return f"{int(num)}" if unit == "B" else f"{num:3.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}T"

def make_index(directory: Path, root: Path) -> None:
    rel = directory.relative_to(root)
    title = f"Index of /{rel}" if str(rel) != "." else "Index of /"

    entries = []
    if directory != root:
        entries.append(("../", "-", "-"))

    for p in sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if p.name.startswith("."):
            continue
        name = p.name + ("/" if p.is_dir() else "")
        if p.is_dir():
            size = "-"
        else:
            try:
                size = human_size(p.stat().st_size)
            except OSError:
                size = "-"
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%d-%b-%Y %H:%M")
        except OSError:
            mtime = "-"
        entries.append((name, mtime, size))

    rows = []
    for href, mtime, size in entries:
        display = href.rstrip("/")
        rows.append(
            f'<tr><td><a href="{href}">{display}</a></td>'
            f'<td align="right">{mtime}</td>'
            f'<td align="right">{size}</td></tr>'
        )

    html = (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        "<html>\n<head>\n"
        f"<title>{title}</title>\n"
        "</head>\n<body>\n"
        f"<h1>{title}</h1>\n"
        "<table>\n"
        "<tr><th>Name</th><th>Last modified</th><th>Size</th></tr>\n"
        '<tr><th colspan="3"><hr></th></tr>\n'
        + "\n".join(rows)
        + '\n<tr><th colspan="3"><hr></th></tr>\n'
        "</table>\n</body>\n</html>\n"
    )

    (directory / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {directory / 'index.html'}")

def main() -> None:
    root = Path("zips")
    if not root.is_dir():
        raise SystemExit(f"{root} does not exist")

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        make_index(Path(dirpath), root)

if __name__ == "__main__":
    main()
